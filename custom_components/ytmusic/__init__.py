"""The YouTube Music integration."""

from __future__ import annotations

import contextlib
import logging
import os
from dataclasses import dataclass

from homeassistant.components.frontend import add_extra_js_url
from homeassistant.components.http import StaticPathConfig
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed, ConfigEntryNotReady
import homeassistant.helpers.issue_registry as ir

from ytmusicapi.auth.oauth import OAuthCredentials

from .api import YtMusicApi
from .auth import build_client
from .const import (
    AUTH_OAUTH,
    CONF_AUTH_METHOD,
    CONF_CLIENT_ID,
    CONF_CLIENT_SECRET,
    CONF_ENTRY_SECRET,
    CONF_OAUTH_TOKEN,
    CONF_STREAM_COOKIE,
    DOMAIN,
    PLATFORMS,
)
from .coordinator import YtMusicCoordinator
from .http import YtMusicStreamView
from .stream import StreamResolver
from .websocket_api import async_register as _register_ws_commands
from .tv.backend import TvBackend
from .tv.errors import TvFormatError

_LOGGER = logging.getLogger(__name__)

# Shared with the single registered view (keyed by entry_id).
STREAM_RESOLVERS: dict[str, StreamResolver] = {}
STREAM_SECRETS: dict[str, str] = {}
_VIEW_REGISTERED = "ytmusic_view_registered"
_CARD_REGISTERED = "ytmusic_card_registered"
_WS_REGISTERED = "ytmusic_ws_registered"
_CARD_URL = "/ytmusic/ytmusic-card.js"
_CARD_VERSION = "0.1.6"  # bump on each card bundle change to bust the frontend cache


@dataclass
class YtMusicRuntimeData:
    api: YtMusicApi
    resolver: StreamResolver
    coordinator: YtMusicCoordinator
    entry_secret: str


type YtMusicConfigEntry = ConfigEntry[YtMusicRuntimeData]


async def _register_view_once(hass: HomeAssistant) -> None:
    if hass.data.get(_VIEW_REGISTERED):
        return
    hass.http.register_view(YtMusicStreamView(STREAM_RESOLVERS, STREAM_SECRETS))
    hass.data[_VIEW_REGISTERED] = True


async def _register_ws_once(hass: HomeAssistant) -> None:
    if hass.data.get(_WS_REGISTERED):
        return
    _register_ws_commands(hass)
    hass.data[_WS_REGISTERED] = True


async def _register_card_once(hass: HomeAssistant) -> None:
    if hass.data.get(_CARD_REGISTERED):
        return
    path = os.path.join(os.path.dirname(__file__), "frontend", "ytmusic-card.js")
    if not await hass.async_add_executor_job(os.path.exists, path):
        return  # card bundle ships in Plan 2; skip until present
    await hass.http.async_register_static_paths(
        [StaticPathConfig(_CARD_URL, path, False)]
    )
    add_extra_js_url(hass, f"{_CARD_URL}?v={_CARD_VERSION}")
    hass.data[_CARD_REGISTERED] = True


async def async_setup_entry(hass: HomeAssistant, entry: YtMusicConfigEntry) -> bool:
    if entry.data.get(CONF_AUTH_METHOD) == AUTH_OAUTH:
        creds = OAuthCredentials(
            client_id=entry.data[CONF_CLIENT_ID],
            client_secret=entry.data[CONF_CLIENT_SECRET],
        )
        api = TvBackend(hass, creds, dict(entry.data[CONF_OAUTH_TOKEN]))
    else:
        try:
            client = await hass.async_add_executor_job(build_client, dict(entry.data))
        except Exception as err:  # noqa: BLE001
            raise ConfigEntryAuthFailed(str(err)) from err
        api = YtMusicApi(hass, client)

    coordinator = YtMusicCoordinator(hass, api)
    # first_refresh converts the coordinator's UpdateFailed -> ConfigEntryNotReady
    # (HA retries on transient errors) and propagates ConfigEntryAuthFailed -> reauth.
    try:
        await coordinator.async_config_entry_first_refresh()
    except ConfigEntryNotReady:
        if isinstance(coordinator.last_exception, TvFormatError):
            ir.async_create_issue(
                hass,
                DOMAIN,
                "tv_format_changed",
                is_fixable=False,
                severity=ir.IssueSeverity.ERROR,
                translation_key="tv_format_changed",
            )
        raise

    cookiefile = None
    if stream_cookie := entry.data.get(CONF_STREAM_COOKIE):
        cookiefile = await hass.async_add_executor_job(
            _write_cookiefile, hass, entry.entry_id, stream_cookie
        )
    resolver = StreamResolver(hass, cookiefile=cookiefile)

    secret = entry.data[CONF_ENTRY_SECRET]
    STREAM_RESOLVERS[entry.entry_id] = resolver
    STREAM_SECRETS[entry.entry_id] = secret
    await _register_view_once(hass)
    await _register_ws_once(hass)
    await _register_card_once(hass)

    entry.runtime_data = YtMusicRuntimeData(
        api=api, resolver=resolver, coordinator=coordinator, entry_secret=secret
    )
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(_async_update_listener))
    return True


async def async_unload_entry(hass: HomeAssistant, entry: YtMusicConfigEntry) -> bool:
    unloaded = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unloaded:
        STREAM_RESOLVERS.pop(entry.entry_id, None)
        STREAM_SECRETS.pop(entry.entry_id, None)
    return unloaded


async def async_remove_entry(hass: HomeAssistant, entry: YtMusicConfigEntry) -> None:
    """Delete the per-entry yt-dlp cookies file, if any."""
    path = hass.config.path(f".storage/ytmusic_cookies_{entry.entry_id}.txt")
    await hass.async_add_executor_job(_remove_file_if_exists, path)


def _remove_file_if_exists(path: str) -> None:
    with contextlib.suppress(FileNotFoundError):
        os.remove(path)


async def _async_update_listener(
    hass: HomeAssistant, entry: YtMusicConfigEntry
) -> None:
    await hass.config_entries.async_reload(entry.entry_id)


def _write_cookiefile(hass: HomeAssistant, entry_id: str, cookie: str) -> str:
    """Write a Netscape cookies.txt for yt-dlp from a raw Cookie header."""
    path = hass.config.path(f".storage/ytmusic_cookies_{entry_id}.txt")
    lines = ["# Netscape HTTP Cookie File"]
    for part in cookie.split(";"):
        part = part.strip()
        if "=" in part:
            name, value = part.split("=", 1)
            lines.append(
                "\t".join(
                    [
                        ".youtube.com",
                        "TRUE",
                        "/",
                        "TRUE",
                        "2147483647",
                        name.strip(),
                        value.strip(),
                    ]
                )
            )
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")
    os.chmod(path, 0o600)
    return path
