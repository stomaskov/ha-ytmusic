"""YouTube Music media_player entity (source/proxy model)."""

from __future__ import annotations

import logging
from datetime import timedelta

from homeassistant.components.media_player import (
    BrowseMedia,
    MediaClass,
    MediaPlayerEntity,
    MediaPlayerEntityFeature,
    MediaPlayerState,
    RepeatMode as HARepeatMode,
    SearchMedia,
    SearchMediaQuery,
)
from homeassistant.core import Event, HomeAssistant, callback
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.event import async_call_later, async_track_state_change_event
from homeassistant.helpers.network import get_url
from homeassistant.util import dt as dt_util

from . import YtMusicConfigEntry
from .const import (
    CONF_AUTOPLAY,
    CONF_DEFAULT_SOURCE,
    DEFAULT_AUTOPLAY,
    STREAM_URL_BASE,
)
from .http import build_stream_path
from .models import RepeatMode, Track
from .queue import PlayQueue

_LOGGER = logging.getLogger(__name__)

# Delay before advancing to the next track when our stream goes idle. Gives a
# foreign app that's mid-handoff (brief idle blip while it claims the speaker)
# time to take over, so we don't fight it by re-pushing our next track.
_ADVANCE_DEBOUNCE_S = 1.2

_SUPPORTED = (
    MediaPlayerEntityFeature.PLAY
    | MediaPlayerEntityFeature.PAUSE
    | MediaPlayerEntityFeature.STOP
    | MediaPlayerEntityFeature.NEXT_TRACK
    | MediaPlayerEntityFeature.PREVIOUS_TRACK
    | MediaPlayerEntityFeature.VOLUME_SET
    | MediaPlayerEntityFeature.SHUFFLE_SET
    | MediaPlayerEntityFeature.REPEAT_SET
    | MediaPlayerEntityFeature.PLAY_MEDIA
    | MediaPlayerEntityFeature.SELECT_SOURCE
    | MediaPlayerEntityFeature.BROWSE_MEDIA
    | MediaPlayerEntityFeature.SEARCH_MEDIA
    | MediaPlayerEntityFeature.VOLUME_MUTE
    | MediaPlayerEntityFeature.SEEK
)

# SearchItem.kind -> (play media_content_type, BrowseMedia media_class)
_KIND_TO_MEDIA = {
    "song": ("music", MediaClass.TRACK),
    "video": ("music", MediaClass.TRACK),
    "playlist": ("playlist", MediaClass.PLAYLIST),
    "album": ("album", MediaClass.ALBUM),
    "artist": ("artist", MediaClass.ARTIST),
}

_REPEAT_TO_HA = {
    RepeatMode.OFF: HARepeatMode.OFF,
    RepeatMode.ONE: HARepeatMode.ONE,
    RepeatMode.ALL: HARepeatMode.ALL,
}
_REPEAT_FROM_HA = {v: k for k, v in _REPEAT_TO_HA.items()}

# Downstream speaker state string -> our mirrored MediaPlayerState.
_SOURCE_STATE_MAP = {
    "playing": MediaPlayerState.PLAYING,
    "paused": MediaPlayerState.PAUSED,
    "buffering": MediaPlayerState.BUFFERING,
    "idle": MediaPlayerState.IDLE,
    "off": MediaPlayerState.OFF,
    "standby": MediaPlayerState.STANDBY,
}


async def async_setup_entry(
    hass: HomeAssistant,
    entry: YtMusicConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    from homeassistant.helpers import config_validation as cv
    from homeassistant.helpers.entity_platform import async_get_current_platform
    import voluptuous as vol

    async_add_entities([YtMusicPlayer(hass, entry)])

    platform = async_get_current_platform()
    track_schema = {
        vol.Required("video_id"): cv.string,
        vol.Optional("title", default=""): cv.string,
        vol.Optional("artist", default=""): cv.string,
    }
    platform.async_register_entity_service("enqueue", track_schema, "svc_enqueue")
    platform.async_register_entity_service("play_next", track_schema, "svc_play_next")
    platform.async_register_entity_service(
        "start_radio", {vol.Required("video_id"): cv.string}, "svc_start_radio"
    )
    platform.async_register_entity_service("clear_queue", {}, "svc_clear_queue")
    platform.async_register_entity_service("disconnect", {}, "svc_disconnect")
    platform.async_register_entity_service(
        "remove", {vol.Required("index"): cv.positive_int}, "svc_remove"
    )
    platform.async_register_entity_service(
        "move",
        {
            vol.Required("from_index"): cv.positive_int,
            vol.Required("to_index"): cv.positive_int,
        },
        "svc_move",
    )
    platform.async_register_entity_service(
        "jump", {vol.Required("index"): cv.positive_int}, "svc_jump"
    )
    platform.async_register_entity_service(
        "set_sleep_timer",
        {
            vol.Optional("minutes"): cv.positive_int,
            vol.Optional("end_of_track", default=False): cv.boolean,
        },
        "svc_set_sleep_timer",
    )


class YtMusicPlayer(MediaPlayerEntity):
    _attr_has_entity_name = True
    _attr_name = None
    _attr_supported_features = _SUPPORTED
    # The queue can be large (radio/long playlists) — keep it live for the UI but
    # don't record it (avoids the 16 KB recorder-attribute limit + DB bloat).
    _unrecorded_attributes = frozenset({"queue", "queue_position"})

    def __init__(self, hass: HomeAssistant, entry: YtMusicConfigEntry) -> None:
        self.hass = hass
        self._entry = entry
        self._api = entry.runtime_data.api
        self._secret = entry.runtime_data.entry_secret
        self._queue = PlayQueue()
        self._source = entry.options.get(CONF_DEFAULT_SOURCE) or None
        self._attr_unique_id = entry.entry_id
        self._active = False  # True while we're driving the speaker with our queue
        self._unsub = None
        self._advance_unsub = None  # pending debounced auto-advance timer
        self._sleep_unsub = None
        self._sleep_ends_at = None
        self._sleep_after_track = False

    # ---- lifecycle ----
    async def async_added_to_hass(self) -> None:
        if self._source:
            self._subscribe()

    def _subscribe(self) -> None:
        if self._unsub:
            self._unsub()
        if self._source:
            self._unsub = async_track_state_change_event(
                self.hass, [self._source], self._handle_source_state
            )

    async def async_will_remove_from_hass(self) -> None:
        self._cancel_sleep()
        self._cancel_pending_advance()
        if self._unsub:
            self._unsub()

    # ---- source selection ----
    @property
    def source(self) -> str | None:
        return self._source

    @property
    def source_list(self) -> list[str]:
        return [
            s.entity_id
            for s in self.hass.states.async_all("media_player")
            if s.entity_id != self.entity_id
        ]

    async def async_select_source(self, source: str) -> None:
        self._source = source
        self._subscribe()
        self.async_write_ha_state()

    # ---- state mirrored from the downstream speaker ----
    @property
    def _source_state(self):
        return self.hass.states.get(self._source) if self._source else None

    @property
    def state(self) -> MediaPlayerState:
        # Reflect the speaker only while we're actively driving it; otherwise idle
        # (so the speaker playing unrelated content doesn't show as our state).
        if not self._active:
            return MediaPlayerState.IDLE
        src = self._source_state
        if src is None or src.state in ("unavailable", "unknown"):
            return MediaPlayerState.IDLE
        return _SOURCE_STATE_MAP.get(src.state, MediaPlayerState.IDLE)

    @property
    def volume_level(self) -> float | None:
        src = self._source_state
        return src.attributes.get("volume_level") if src else None

    @property
    def is_volume_muted(self) -> bool | None:
        src = self._source_state
        return src.attributes.get("is_volume_muted") if src else None

    @property
    def media_position(self) -> int | None:
        if not self._active:
            return None
        src = self._source_state
        return src.attributes.get("media_position") if src else None

    @property
    def media_position_updated_at(self):
        if not self._active:
            return None
        src = self._source_state
        return src.attributes.get("media_position_updated_at") if src else None

    @property
    def media_duration(self) -> int | None:
        src = self._source_state
        dur = src.attributes.get("media_duration") if src else None
        if dur is not None:
            return dur
        cur = self._queue.current()
        return cur.duration if cur else None

    # ---- now playing ----
    @property
    def media_title(self) -> str | None:
        cur = self._queue.current()
        return cur.title if cur else None

    @property
    def media_artist(self) -> str | None:
        cur = self._queue.current()
        return cur.artists if cur else None

    @property
    def media_image_url(self) -> str | None:
        cur = self._queue.current()
        return cur.thumbnail if cur else None

    @property
    def shuffle(self) -> bool:
        return self._queue.shuffle

    @property
    def repeat(self) -> HARepeatMode:
        return _REPEAT_TO_HA[self._queue.repeat]

    @property
    def extra_state_attributes(self) -> dict:
        return {
            "queue": self._queue.as_list(),
            "queue_position": self._queue.index,
            "typed_search": getattr(self._api, "typed_search", False),
            "lyrics_supported": getattr(self._api, "lyrics_supported", False),
            "sleep_timer_ends_at": (
                self._sleep_ends_at.isoformat() if self._sleep_ends_at else None
            ),
            "sleep_timer_end_of_track": self._sleep_after_track,
        }

    # ---- play ----
    async def async_play_media(self, media_type: str, media_id: str, **kwargs) -> None:
        if media_type in ("track", "music"):
            tracks = [self._track_from_kwargs(media_id, kwargs)]
        elif media_type == "playlist":
            tracks = await self._api.get_playlist_tracks(media_id)
        elif media_type == "album":
            tracks = await self._api.get_album_tracks(media_id)
        elif media_type == "artist":
            tracks = await self._api.get_artist_songs(media_id)
        else:
            raise HomeAssistantError(f"Unsupported media type: {media_type}")
        if not tracks:
            return
        self._queue.set_queue(tracks)
        await self._push_current()

    def _track_from_kwargs(self, video_id: str, kwargs: dict) -> Track:
        meta = (kwargs.get("extra") or {}).get("metadata") or {}
        return Track(
            video_id=video_id,
            title=meta.get("title", ""),
            artists=meta.get("artist", ""),
            album=meta.get("album"),
            thumbnail=meta.get("thumbnail"),
            duration=meta.get("duration"),
        )

    def _is_our_content(self, state) -> bool:
        """True if the speaker is playing one of our signed stream URLs."""
        if state is None:
            return False
        cid = state.attributes.get("media_content_id") or ""
        return f"{STREAM_URL_BASE}/{self._entry.entry_id}" in cid

    async def _push_current(self) -> None:
        self._cancel_pending_advance()
        cur = self._queue.current()
        if not cur or not self._source:
            return
        base = get_url(self.hass, prefer_external=False, allow_internal=True)
        url = base + build_stream_path(self._entry.entry_id, cur.video_id, self._secret)
        await self.hass.services.async_call(
            "media_player",
            "play_media",
            {
                "entity_id": self._source,
                "media_content_id": url,
                "media_content_type": "music",
                "extra": {"title": cur.title, "thumb": cur.thumbnail},
            },
            blocking=False,
        )
        self._active = True
        self.async_write_ha_state()

    async def _advance(self) -> None:
        # Bail if a foreign app grabbed the speaker while we waited to advance —
        # don't reclaim it from under them.
        src = self._source_state
        if src is not None and src.state == "playing" and not self._is_our_content(src):
            self._active = False
            self.async_write_ha_state()
            return
        last = self._queue.current()
        nxt = self._queue.next()
        if (
            nxt is None
            and self._entry.options.get(CONF_AUTOPLAY, DEFAULT_AUTOPLAY)
            and last
        ):
            radio = await self._api.get_radio(last.video_id)
            if radio:
                self._queue.enqueue(radio)
                nxt = self._queue.next()
        if nxt is None:
            self._active = False
            self.async_write_ha_state()
            return
        await self._push_current()

    @callback
    def _handle_source_state(self, event: Event) -> None:
        new = event.data.get("new_state")
        if new is None:
            return
        if self._active:
            old = event.data.get("old_state")
            if new.state == "playing" and not self._is_our_content(new):
                # Another app (or the user) took over the speaker — stop driving
                # it so casting from elsewhere works. Re-select a speaker to resume.
                self._cancel_pending_advance()
                self._active = False
            elif (
                old is not None
                and old.state == "playing"
                and new.state == "idle"
                and self._is_our_content(old)
            ):
                # Our track ended — advance after a short debounce so a foreign app
                # mid-handoff can claim the speaker instead of us re-grabbing it.
                self._schedule_advance()
        self.async_write_ha_state()

    def _cancel_pending_advance(self) -> None:
        if self._advance_unsub:
            self._advance_unsub()
            self._advance_unsub = None

    def _schedule_advance(self) -> None:
        self._cancel_pending_advance()
        self._advance_unsub = async_call_later(
            self.hass, _ADVANCE_DEBOUNCE_S, self._advance_fire
        )

    @callback
    def _advance_fire(self, _now) -> None:
        self._advance_unsub = None
        if self._sleep_after_track:
            self._cancel_sleep()
            self.hass.async_create_task(self._sleep_pause())
        else:
            self.hass.async_create_task(self._advance())

    # ---- transport (passthrough) ----
    async def _source_call(self, service: str, data: dict | None = None) -> None:
        if not self._source:
            return
        await self.hass.services.async_call(
            "media_player",
            service,
            {"entity_id": self._source, **(data or {})},
            blocking=False,
        )

    async def async_media_play(self) -> None:
        await self._source_call("media_play")

    async def async_media_pause(self) -> None:
        await self._source_call("media_pause")

    async def async_media_stop(self) -> None:
        self._cancel_pending_advance()
        self._active = False
        self.async_write_ha_state()
        await self._source_call("media_stop")

    async def async_media_next_track(self) -> None:
        await self._advance()

    async def async_media_previous_track(self) -> None:
        if self._queue.previous():
            await self._push_current()

    async def async_set_volume_level(self, volume: float) -> None:
        await self._source_call("volume_set", {"volume_level": volume})

    async def async_mute_volume(self, mute: bool) -> None:
        await self._source_call("volume_mute", {"is_volume_muted": mute})

    async def async_media_seek(self, position: float) -> None:
        await self._source_call("media_seek", {"seek_position": position})

    async def async_set_shuffle(self, shuffle: bool) -> None:
        self._queue.set_shuffle(shuffle)
        self.async_write_ha_state()

    async def async_set_repeat(self, repeat: HARepeatMode) -> None:
        self._queue.set_repeat(_REPEAT_FROM_HA[repeat])
        self.async_write_ha_state()

    # ---- browse ----
    async def async_browse_media(self, media_content_type=None, media_content_id=None):
        from .browse import async_browse  # local import to keep entity lean

        return await async_browse(self, media_content_type, media_content_id)

    async def async_search_media(self, query: SearchMediaQuery) -> SearchMedia:
        items = await self._api.search(query.search_query, "songs")
        results = []
        for item in items:
            ctype, mclass = _KIND_TO_MEDIA.get(item.kind, ("music", MediaClass.TRACK))
            results.append(
                BrowseMedia(
                    title=item.title,
                    media_class=mclass,
                    media_content_type=ctype,
                    media_content_id=item.id,
                    can_play=True,
                    can_expand=item.kind in ("playlist", "album", "artist"),
                    thumbnail=item.thumbnail,
                )
            )
        return SearchMedia(result=results)

    # ---- custom service handlers ----
    def _mk(self, video_id: str, title: str | None, artist: str | None) -> Track:
        return Track(video_id, title or "", artist or "", None, None, None)

    async def svc_enqueue(
        self, video_id: str, title: str = "", artist: str = ""
    ) -> None:
        self._queue.enqueue([self._mk(video_id, title, artist)])
        self.async_write_ha_state()

    async def svc_play_next(
        self, video_id: str, title: str = "", artist: str = ""
    ) -> None:
        self._queue.enqueue_next([self._mk(video_id, title, artist)])
        self.async_write_ha_state()

    async def svc_start_radio(self, video_id: str) -> None:
        radio = await self._api.get_radio(video_id)
        if radio:
            self._queue.set_queue(radio)
            await self._push_current()

    async def svc_clear_queue(self) -> None:
        self._cancel_sleep()
        self._queue.clear()
        self.async_write_ha_state()

    async def svc_disconnect(self) -> None:
        """Stop playback and release the speaker so other apps can cast to it."""
        self._cancel_sleep()
        self._cancel_pending_advance()
        was_active = self._active
        self._active = False
        if self._source and was_active:
            await self._source_call("media_stop")
        if self._unsub:
            self._unsub()
            self._unsub = None
        self._source = None
        self.async_write_ha_state()

    async def svc_remove(self, index: int) -> None:
        self._queue.remove(index)
        self.async_write_ha_state()

    async def svc_move(self, from_index: int, to_index: int) -> None:
        self._queue.move(from_index, to_index)
        self.async_write_ha_state()

    async def svc_jump(self, index: int) -> None:
        if self._queue.jump(index) is not None:
            await self._push_current()

    # ---- sleep timer ----
    def _cancel_sleep(self) -> None:
        if self._sleep_unsub:
            self._sleep_unsub()
            self._sleep_unsub = None
        self._sleep_ends_at = None
        self._sleep_after_track = False

    @callback
    def _sleep_fire(self, _now) -> None:
        self._sleep_unsub = None
        self._sleep_ends_at = None
        self.hass.async_create_task(self._sleep_pause())

    async def _sleep_pause(self) -> None:
        self._active = False
        await self._source_call("media_pause")
        self.async_write_ha_state()

    async def svc_set_sleep_timer(
        self, minutes: int | None = None, end_of_track: bool = False
    ) -> None:
        self._cancel_sleep()
        if end_of_track:
            self._sleep_after_track = True
        elif minutes:
            delay = minutes * 60
            self._sleep_ends_at = dt_util.utcnow() + timedelta(seconds=delay)
            self._sleep_unsub = async_call_later(self.hass, delay, self._sleep_fire)
        self.async_write_ha_state()
