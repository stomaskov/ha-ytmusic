from unittest.mock import AsyncMock, patch

from homeassistant.helpers import entity_registry as er
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.ytmusic import websocket_api as ws
from custom_components.ytmusic.backend import SearchItem
from custom_components.ytmusic.models import LyricLine, LyricsResult, Track
from custom_components.ytmusic.const import (
    AUTH_COOKIE,
    CONF_AUTH_METHOD,
    CONF_COOKIE,
    CONF_ENTRY_SECRET,
    DOMAIN,
)

_COOKIE = "SAPISID=abc; __Secure-3PAPISID=def; __Secure-3PSID=ghi"


async def test_do_search_serializes_items():
    api = AsyncMock()
    api.search.return_value = [
        SearchItem(kind="song", id="v1", title="S", subtitle="A", thumbnail="t"),
    ]
    out = await ws._do_search(api, "daft", "songs")
    assert out == {
        "results": [
            {"kind": "song", "id": "v1", "title": "S", "subtitle": "A", "thumbnail": "t"}
        ]
    }
    api.search.assert_awaited_once_with("daft", "songs")


async def _setup_cookie_entry(hass, fake_api):
    entry = MockConfigEntry(
        domain=DOMAIN,
        data={CONF_AUTH_METHOD: AUTH_COOKIE, CONF_COOKIE: _COOKIE, CONF_ENTRY_SECRET: "deadbeef"},
        options={},
    )
    entry.add_to_hass(hass)
    with (
        patch("custom_components.ytmusic.build_client", return_value=object()),
        patch("custom_components.ytmusic.YtMusicApi", return_value=fake_api),
        patch("custom_components.ytmusic.add_extra_js_url"),
    ):
        assert await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()
    ents = er.async_entries_for_config_entry(er.async_get(hass), entry.entry_id)
    return ents[0].entity_id


async def test_ws_search_end_to_end(hass, hass_ws_client):
    fake_api = AsyncMock()
    fake_api.get_library_playlists.return_value = []
    fake_api.search.return_value = [
        SearchItem(kind="song", id="v1", title="S", subtitle="A", thumbnail="t"),
    ]
    entity_id = await _setup_cookie_entry(hass, fake_api)

    client = await hass_ws_client(hass)
    await client.send_json({"id": 1, "type": "ytmusic/search", "entity_id": entity_id, "query": "daft"})
    msg = await client.receive_json()
    assert msg["success"]
    assert msg["result"]["results"][0]["id"] == "v1"
    fake_api.search.assert_awaited_once_with("daft", "songs")


async def test_ws_search_unknown_entity_errors(hass, hass_ws_client):
    # Register commands without a full entry setup.
    ws.async_register(hass)
    client = await hass_ws_client(hass)
    await client.send_json({"id": 1, "type": "ytmusic/search", "entity_id": "media_player.nope", "query": "x"})
    msg = await client.receive_json()
    assert not msg["success"]
    assert msg["error"]["code"] == "not_found"


async def test_do_browse_root_returns_playlists():
    api = AsyncMock()
    api.get_library_playlists.return_value = [{"id": "PL1", "title": "Mix", "thumbnail": "t"}]
    out = await ws._do_browse(api, None, None)
    assert out == {
        "items": [
            {"id": "PL1", "title": "Mix", "thumbnail": "t", "kind": "playlist", "can_expand": True}
        ]
    }


async def test_do_browse_drilldown_returns_tracks():
    api = AsyncMock()
    api.get_playlist_tracks.return_value = [Track("v1", "T", "A", "Alb", "th", 100)]
    out = await ws._do_browse(api, "playlist", "PL1")
    api.get_playlist_tracks.assert_awaited_once_with("PL1")
    assert out["items"][0]["video_id"] == "v1"
    assert out["items"][0]["kind"] == "song"


async def test_do_browse_unknown_type_is_empty():
    api = AsyncMock()
    assert await ws._do_browse(api, "bogus", "x") == {"items": []}


async def test_do_lyrics_present():
    api = AsyncMock()
    api.get_lyrics.return_value = LyricsResult([LyricLine("hi", 0)], synced=True)
    out = await ws._do_lyrics(api, "v1")
    assert out == {"lines": [{"text": "hi", "start_ms": 0}], "synced": True}


async def test_do_lyrics_absent():
    api = AsyncMock()
    api.get_lyrics.return_value = None
    assert await ws._do_lyrics(api, "v1") == {"lines": None, "synced": False}
