"""Async wrapper around ytmusicapi. Every call runs in the executor."""

from __future__ import annotations

import logging
from functools import partial

from homeassistant.core import HomeAssistant

from .backend import SearchItem
from .models import LyricLine, LyricsResult, Track

_LOGGER = logging.getLogger(__name__)


def _browse_kind(bid: str) -> str:
    """Infer content kind from a browseId prefix."""
    if bid.startswith("MPRE"):
        return "album"
    if bid.startswith("UC"):
        return "artist"
    return "playlist"


def _parse_lyrics(data) -> LyricsResult | None:
    if not isinstance(data, dict):
        return None
    lyr = data.get("lyrics")
    if lyr is None:
        return None
    if isinstance(lyr, str):
        lines = [LyricLine(ln) for ln in lyr.splitlines() if ln.strip()]
        return LyricsResult(lines=lines, synced=False) if lines else None
    out: list[LyricLine] = []
    for item in lyr:
        if isinstance(item, dict):
            text, start = item.get("text", ""), item.get("start_time")
        else:
            text, start = getattr(item, "text", ""), getattr(item, "start_time", None)
        if text:
            out.append(LyricLine(text, int(start) if start is not None else None))
    if not out:
        return None
    return LyricsResult(lines=out, synced=any(ln.start_ms is not None for ln in out))


class YtMusicApi:
    typed_search = True
    lyrics_supported = True

    def __init__(self, hass: HomeAssistant, client) -> None:
        self._hass = hass
        self._client = client

    async def _run(self, func, *args, **kwargs):
        return await self._hass.async_add_executor_job(partial(func, *args, **kwargs))

    @staticmethod
    def _thumb(item: dict) -> str | None:
        thumbs = item.get("thumbnails") or []
        return thumbs[-1]["url"] if thumbs else None

    @classmethod
    def _to_track(cls, item: dict) -> Track:
        artists = ", ".join(
            a["name"] for a in (item.get("artists") or []) if a.get("name")
        )
        album = (
            (item.get("album") or {}).get("name")
            if isinstance(item.get("album"), dict)
            else None
        )
        return Track(
            video_id=item.get("videoId", ""),
            title=item.get("title", ""),
            artists=artists,
            album=album,
            thumbnail=cls._thumb(item),
            duration=item.get("duration_seconds"),
        )

    async def validate(self) -> None:
        await self.get_library_playlists()

    async def search(self, query: str, filter: str) -> list[SearchItem]:  # noqa: A002
        results = await self._run(self._client.search, query, filter=filter)
        out: list[SearchItem] = []
        for r in results:
            vid = r.get("videoId")
            bid = r.get("browseId")
            if not vid and not bid:
                continue
            artists = ", ".join(
                a["name"] for a in (r.get("artists") or []) if a.get("name")
            )
            out.append(
                SearchItem(
                    kind="song" if vid else _browse_kind(bid),
                    id=vid or bid,
                    title=r.get("title", ""),
                    subtitle=artists,
                    thumbnail=self._thumb(r),
                )
            )
        return out

    async def get_library_playlists(self) -> list[dict]:
        rows = await self._run(self._client.get_library_playlists)
        return [
            {
                "id": r["playlistId"],
                "title": r.get("title", ""),
                "thumbnail": self._thumb(r),
            }
            for r in rows
        ]

    async def get_playlist_tracks(self, playlist_id: str) -> list[Track]:
        data = await self._run(self._client.get_playlist, playlist_id)
        return [self._to_track(t) for t in data.get("tracks", []) if t.get("videoId")]

    async def get_album_tracks(self, browse_id: str) -> list[Track]:
        data = await self._run(self._client.get_album, browse_id)
        return [self._to_track(t) for t in data.get("tracks", []) if t.get("videoId")]

    async def get_artist_songs(self, channel_id: str) -> list[Track]:
        data = await self._run(self._client.get_artist, channel_id)
        songs = (data.get("songs") or {}).get("results", [])
        return [self._to_track(t) for t in songs if t.get("videoId")]

    async def get_radio(self, video_id: str) -> list[Track]:
        data = await self._run(
            self._client.get_watch_playlist, videoId=video_id, radio=True
        )
        return [self._to_track(t) for t in data.get("tracks", []) if t.get("videoId")]

    async def get_lyrics(self, video_id: str) -> LyricsResult | None:
        wp = await self._run(self._client.get_watch_playlist, videoId=video_id)
        browse_id = wp.get("lyrics") if isinstance(wp, dict) else None
        if not browse_id:
            return None
        try:
            data = await self._run(self._client.get_lyrics, browse_id, True)
        except Exception:  # noqa: BLE001 — older ytmusicapi may reject timestamps=True
            _LOGGER.debug(
                "timestamped lyrics fetch failed; retrying without timestamps",
                exc_info=True,
            )
            data = await self._run(self._client.get_lyrics, browse_id)
        return _parse_lyrics(data)
