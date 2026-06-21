"""WebSocket API consumed by the ytmusic dashboard cards."""

from __future__ import annotations

import voluptuous as vol

from homeassistant.components import websocket_api
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er

from .backend import MusicBackend
from .const import DOMAIN, SEARCH_FILTERS


def _entry_api(hass: HomeAssistant, entity_id: str) -> MusicBackend | None:
    """Resolve a ytmusic entity_id to its active backend."""
    ent = er.async_get(hass).async_get(entity_id)
    if ent is None or ent.platform != DOMAIN or ent.config_entry_id is None:
        return None
    entry = hass.config_entries.async_get_entry(ent.config_entry_id)
    runtime = getattr(entry, "runtime_data", None) if entry else None
    return runtime.api if runtime else None


async def _do_search(api: MusicBackend, query: str, filter: str) -> dict:  # noqa: A002
    items = await api.search(query, filter)
    return {"results": [i.as_dict() for i in items]}


async def _do_lyrics(api: MusicBackend, video_id: str) -> dict:
    res = await api.get_lyrics(video_id)
    return res.as_dict() if res else {"lines": None, "synced": False}


async def _do_browse(api: MusicBackend, item_type: str | None, item_id: str | None) -> dict:
    if not item_id:
        return {
            "items": [
                {**p, "kind": "playlist", "can_expand": True}
                for p in await api.get_library_playlists()
            ]
        }
    fetch = {
        "playlist": api.get_playlist_tracks,
        "album": api.get_album_tracks,
        "artist": api.get_artist_songs,
    }.get(item_type)
    if fetch is None:
        return {"items": []}
    return {"items": [{**t.as_dict(), "kind": "song"} for t in await fetch(item_id)]}


@websocket_api.websocket_command(
    {
        vol.Required("type"): "ytmusic/search",
        vol.Required("entity_id"): str,
        vol.Required("query"): str,
        vol.Optional("filter", default="songs"): vol.In(SEARCH_FILTERS),
    }
)
@websocket_api.async_response
async def ws_search(hass, connection, msg) -> None:
    api = _entry_api(hass, msg["entity_id"])
    if api is None:
        connection.send_error(msg["id"], "not_found", f"Unknown ytmusic entity {msg['entity_id']}")
        return
    connection.send_result(msg["id"], await _do_search(api, msg["query"], msg["filter"]))


@websocket_api.websocket_command(
    {
        vol.Required("type"): "ytmusic/browse",
        vol.Required("entity_id"): str,
        vol.Optional("item_type"): vol.In(["playlist", "album", "artist"]),
        vol.Optional("item_id"): str,
    }
)
@websocket_api.async_response
async def ws_browse(hass, connection, msg) -> None:
    api = _entry_api(hass, msg["entity_id"])
    if api is None:
        connection.send_error(msg["id"], "not_found", f"Unknown ytmusic entity {msg['entity_id']}")
        return
    result = await _do_browse(api, msg.get("item_type"), msg.get("item_id"))
    connection.send_result(msg["id"], result)


@websocket_api.websocket_command(
    {
        vol.Required("type"): "ytmusic/lyrics",
        vol.Required("entity_id"): str,
        vol.Required("video_id"): str,
    }
)
@websocket_api.async_response
async def ws_lyrics(hass, connection, msg) -> None:
    api = _entry_api(hass, msg["entity_id"])
    if api is None:
        connection.send_error(msg["id"], "not_found", f"Unknown ytmusic entity {msg['entity_id']}")
        return
    connection.send_result(msg["id"], await _do_lyrics(api, msg["video_id"]))


def async_register(hass: HomeAssistant) -> None:
    websocket_api.async_register_command(hass, ws_search)
    websocket_api.async_register_command(hass, ws_browse)
    websocket_api.async_register_command(hass, ws_lyrics)
