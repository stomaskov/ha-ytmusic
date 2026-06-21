import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from homeassistant.components.media_player import MediaPlayerState, SearchMediaQuery
from homeassistant.core import HomeAssistant, State
from homeassistant.exceptions import HomeAssistantError

from custom_components.ytmusic.backend import SearchItem
from custom_components.ytmusic.media_player import YtMusicPlayer
from custom_components.ytmusic.models import Track

_HA_SVC_CALL = "homeassistant.core.ServiceRegistry.async_call"


def _track(vid="v1"):
    return Track(vid, "T", "A", None, None, 100)


def _make_player(hass):
    api = AsyncMock()
    runtime = MagicMock()
    runtime.api = api
    runtime.entry_secret = "sek"
    entry = MagicMock()
    entry.entry_id = "e1"
    entry.runtime_data = runtime
    entry.options = {"default_source": "media_player.speaker", "autoplay": True}
    player = YtMusicPlayer(hass, entry)
    player.hass = hass
    player.async_write_ha_state = MagicMock()
    return player, api


async def test_play_track_pushes_proxy_url_to_source(hass: HomeAssistant):
    player, api = _make_player(hass)
    api.get_radio.return_value = []
    with (
        patch(
            "custom_components.ytmusic.media_player.get_url",
            return_value="http://ha:8123",
        ),
        patch(_HA_SVC_CALL, new=AsyncMock()) as call,
    ):
        await player.async_play_media("track", "v1", extra={"metadata": {"title": "T"}})
    # the queue now holds the track and a play_media call went to the speaker
    assert player._queue.current().video_id == "v1"
    args = call.await_args_list[-1].args
    assert args[0] == "media_player"
    assert args[1] == "play_media"
    data = call.await_args_list[-1].args[2]
    assert data["entity_id"] == "media_player.speaker"
    assert "/api/ytmusic/stream/e1/v1/" in data["media_content_id"]


async def test_play_playlist_builds_queue(hass: HomeAssistant):
    player, api = _make_player(hass)
    api.get_playlist_tracks.return_value = [_track("a"), _track("b")]
    with (
        patch(
            "custom_components.ytmusic.media_player.get_url",
            return_value="http://ha:8123",
        ),
        patch(_HA_SVC_CALL, new=AsyncMock()),
    ):
        await player.async_play_media("playlist", "PL1")
    assert [t.video_id for t in player._queue._items] == ["a", "b"]
    assert player._queue.current().video_id == "a"


async def test_advance_radio_at_queue_end(hass: HomeAssistant):
    player, api = _make_player(hass)
    api.get_radio.return_value = [_track("r1")]
    player._queue.set_queue([_track("only")])
    with (
        patch(
            "custom_components.ytmusic.media_player.get_url",
            return_value="http://ha:8123",
        ),
        patch(_HA_SVC_CALL, new=AsyncMock()),
    ):
        await player._advance()
    # radio appended and now playing r1
    assert player._queue.current().video_id == "r1"
    api.get_radio.assert_awaited_once_with("only")


async def test_next_track_at_end_triggers_radio(hass):
    player, api = _make_player(hass)
    api.get_radio.return_value = [_track("r1")]
    player._queue.set_queue([_track("only")])
    with (
        patch(
            "custom_components.ytmusic.media_player.get_url",
            return_value="http://ha:8123",
        ),
        patch(_HA_SVC_CALL, new=AsyncMock()),
    ):
        await player.async_media_next_track()
    assert player._queue.current().video_id == "r1"
    api.get_radio.assert_awaited_once_with("only")


async def test_no_advance_on_startup_idle(hass):
    player, api = _make_player(hass)
    player._queue.set_queue([_track("a"), _track("b")])
    player._active = True
    event = MagicMock()
    event.data = {
        "old_state": State("media_player.speaker", "buffering"),
        "new_state": State("media_player.speaker", "idle"),
    }
    player._handle_source_state(event)
    await hass.async_block_till_done()
    assert player._queue.current().video_id == "a"  # no spurious advance


async def test_advance_on_playing_to_idle(hass):
    player, api = _make_player(hass)
    api.get_radio.return_value = []
    player._queue.set_queue([_track("a"), _track("b")])
    player._active = True
    with (
        patch(
            "custom_components.ytmusic.media_player.get_url",
            return_value="http://ha:8123",
        ),
        patch("homeassistant.core.ServiceRegistry.async_call", new=AsyncMock()),
    ):
        event = MagicMock()
        event.data = {
            "old_state": State("media_player.speaker", "playing"),
            "new_state": State("media_player.speaker", "idle"),
        }
        player._handle_source_state(event)
        await hass.async_block_till_done()
    assert player._queue.current().video_id == "b"


async def test_play_media_music_alias(hass):
    player, api = _make_player(hass)
    with (
        patch(
            "custom_components.ytmusic.media_player.get_url",
            return_value="http://ha:8123",
        ),
        patch("homeassistant.core.ServiceRegistry.async_call", new=AsyncMock()),
    ):
        await player.async_play_media("music", "v1", extra={"metadata": {"title": "T"}})
    assert player._queue.current().video_id == "v1"


async def test_play_media_unknown_type_raises(hass):
    player, api = _make_player(hass)
    with pytest.raises(HomeAssistantError):
        await player.async_play_media("podcast", "x")


async def test_async_search_media_maps_results(hass: HomeAssistant):
    player, api = _make_player(hass)
    api.search.return_value = [
        SearchItem(kind="song", id="v1", title="S", subtitle="A", thumbnail="t"),
        SearchItem(kind="album", id="MPRE1", title="Alb", subtitle="A", thumbnail=None),
    ]
    res = await player.async_search_media(SearchMediaQuery(search_query="daft"))
    assert [r.media_content_id for r in res.result] == ["v1", "MPRE1"]
    assert res.result[0].media_content_type == "music" and res.result[0].can_play
    assert res.result[1].media_content_type == "album" and res.result[1].can_expand
    api.search.assert_awaited_once_with("daft", "songs")


async def test_state_mirrors_source_when_active(hass: HomeAssistant):
    player, api = _make_player(hass)
    hass.states.async_set("media_player.speaker", "paused", {"volume_level": 0.4})
    player._active = True
    assert player.state == MediaPlayerState.PAUSED  # pause -> resume button works
    assert player.volume_level == 0.4  # anchors the volume slider


async def test_state_idle_when_not_active(hass: HomeAssistant):
    player, api = _make_player(hass)
    hass.states.async_set("media_player.speaker", "playing", {})
    # not driving the speaker -> we report idle even if the speaker plays other content
    assert player.state == MediaPlayerState.IDLE


async def test_media_position_and_duration_mirror_source(hass: HomeAssistant):
    player, api = _make_player(hass)
    player._active = True
    hass.states.async_set(
        "media_player.speaker",
        "playing",
        {"media_position": 42, "media_duration": 200},
    )
    assert player.media_position == 42
    assert player.media_duration == 200


async def test_media_position_none_when_not_active(hass: HomeAssistant):
    player, api = _make_player(hass)
    player._active = False
    hass.states.async_set("media_player.speaker", "playing", {"media_position": 42})
    assert player.media_position is None


async def test_media_duration_falls_back_to_track(hass: HomeAssistant):
    player, api = _make_player(hass)
    player._active = True
    player._queue.set_queue([Track("v", "T", "A", None, None, 180)])
    hass.states.async_set("media_player.speaker", "playing", {})
    assert player.media_duration == 180


async def test_mute_passthrough(hass: HomeAssistant):
    player, api = _make_player(hass)
    with patch(_HA_SVC_CALL, new=AsyncMock()) as call:
        await player.async_mute_volume(True)
    args = call.await_args_list[-1].args
    assert args[1] == "volume_mute"
    assert args[2]["entity_id"] == "media_player.speaker"
    assert args[2]["is_volume_muted"] is True


async def test_seek_passthrough(hass: HomeAssistant):
    player, api = _make_player(hass)
    with patch(_HA_SVC_CALL, new=AsyncMock()) as call:
        await player.async_media_seek(33.0)
    args = call.await_args_list[-1].args
    assert args[1] == "media_seek"
    assert args[2]["seek_position"] == 33.0


async def test_supports_mute_and_seek():
    from custom_components.ytmusic.media_player import _SUPPORTED
    from homeassistant.components.media_player import MediaPlayerEntityFeature as F
    assert _SUPPORTED & F.VOLUME_MUTE
    assert _SUPPORTED & F.SEEK


async def test_capability_attributes_reflect_backend(hass: HomeAssistant):
    player, api = _make_player(hass)
    player._api.typed_search = True
    player._api.lyrics_supported = False
    attrs = player.extra_state_attributes
    assert attrs["typed_search"] is True
    assert attrs["lyrics_supported"] is False
