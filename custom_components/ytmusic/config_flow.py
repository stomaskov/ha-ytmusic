"""Config and options flow for YouTube Music."""

from __future__ import annotations

import logging
import secrets
import time
from typing import Any

import voluptuous as vol
from ytmusicapi.auth.oauth import OAuthCredentials

from homeassistant.config_entries import (
    ConfigEntry,
    ConfigFlow,
    ConfigFlowResult,
    OptionsFlow,
)
from homeassistant.core import callback
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers import selector

from .api import YtMusicApi
from .auth import build_client
from .const import (
    AUTH_COOKIE,
    AUTH_OAUTH,
    CONF_AUTH_METHOD,
    CONF_AUTOPLAY,
    CONF_CLIENT_ID,
    CONF_CLIENT_SECRET,
    CONF_COOKIE,
    CONF_DEFAULT_SOURCE,
    CONF_ENTRY_SECRET,
    CONF_OAUTH_TOKEN,
    CONF_RESULT_LIMIT,
    CONF_STREAM_COOKIE,
    DEFAULT_AUTOPLAY,
    DEFAULT_RESULT_LIMIT,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)


async def _validate(hass, data: dict) -> None:
    """Build the matching backend and confirm auth works. Raises on failure.

    OAuth must validate via the TV backend (TVHTML5 context) — the cookie/ytmusicapi
    path returns HTTP 400 for an OAuth token (WEB_REMIX context mismatch).
    """
    if data.get(CONF_AUTH_METHOD) == AUTH_OAUTH:
        from .tv.backend import TvBackend

        creds = OAuthCredentials(
            client_id=data[CONF_CLIENT_ID], client_secret=data[CONF_CLIENT_SECRET]
        )
        await TvBackend(hass, creds, dict(data[CONF_OAUTH_TOKEN])).validate()
        return
    client = await hass.async_add_executor_job(build_client, data)
    api = YtMusicApi(hass, client)
    await api.get_library_playlists()


class YtMusicConfigFlow(ConfigFlow, domain=DOMAIN):
    VERSION = 1

    def __init__(self) -> None:
        self._data: dict[str, Any] = {}
        self._creds: OAuthCredentials | None = None
        self._device_code: str | None = None
        self._oauth_prompt: str = ""

    async def async_step_user(self, user_input=None) -> ConfigFlowResult:
        return self.async_show_menu(
            step_id="user", menu_options=[AUTH_OAUTH, AUTH_COOKIE]
        )

    # ---- OAuth ----
    async def async_step_oauth(self, user_input=None) -> ConfigFlowResult:
        return await self.async_step_oauth_creds()

    async def async_step_oauth_creds(self, user_input=None) -> ConfigFlowResult:
        if user_input is not None:
            self._data[CONF_AUTH_METHOD] = AUTH_OAUTH
            self._data[CONF_CLIENT_ID] = user_input[CONF_CLIENT_ID]
            self._data[CONF_CLIENT_SECRET] = user_input[CONF_CLIENT_SECRET]
            self._creds = OAuthCredentials(
                client_id=user_input[CONF_CLIENT_ID],
                client_secret=user_input[CONF_CLIENT_SECRET],
            )
            code = await self.hass.async_add_executor_job(self._creds.get_code)
            self._device_code = code["device_code"]
            self._oauth_prompt = (
                f"Visit {code['verification_url']} and enter code: {code['user_code']}"
            )
            return await self.async_step_oauth_device()
        return self.async_show_form(
            step_id="oauth_creds",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_CLIENT_ID): str,
                    vol.Required(CONF_CLIENT_SECRET): str,
                }
            ),
        )

    async def async_step_oauth_device(self, user_input=None) -> ConfigFlowResult:
        if user_input is not None:
            try:
                token = await self.hass.async_add_executor_job(
                    self._creds.token_from_code, self._device_code
                )
            except Exception:  # noqa: BLE001
                return self.async_show_form(
                    step_id="oauth_device",
                    description_placeholders={"prompt": self._oauth_prompt},
                    errors={"base": "oauth_pending"},
                )
            if "expires_at" not in token and "expires_in" in token:
                token["expires_at"] = int(time.time()) + int(token["expires_in"])
            self._data[CONF_OAUTH_TOKEN] = token
            return await self._finish_auth()
        return self.async_show_form(
            step_id="oauth_device",
            data_schema=vol.Schema({}),
            description_placeholders={"prompt": self._oauth_prompt},
        )

    # ---- Cookie ----
    async def async_step_cookie(self, user_input=None) -> ConfigFlowResult:
        errors: dict[str, str] = {}
        if user_input is not None:
            self._data[CONF_AUTH_METHOD] = AUTH_COOKIE
            self._data[CONF_COOKIE] = user_input[CONF_COOKIE]
            return await self._finish_auth()
        return self.async_show_form(
            step_id="cookie",
            data_schema=vol.Schema({vol.Required(CONF_COOKIE): str}),
            errors=errors,
        )

    # ---- Shared: validate then optional stream cookie ----
    async def _finish_auth(self, errors: dict | None = None) -> ConfigFlowResult:
        errors = errors or {}
        try:
            await _validate(self.hass, self._data)
        except Exception as err:  # noqa: BLE001
            _LOGGER.warning("YTMusic auth validation failed: %s", err)
            errors["base"] = "auth_failed"
            step = (
                "cookie"
                if self._data[CONF_AUTH_METHOD] == AUTH_COOKIE
                else "oauth_creds"
            )
            schema = (
                vol.Schema({vol.Required(CONF_COOKIE): str})
                if step == "cookie"
                else vol.Schema(
                    {
                        vol.Required(CONF_CLIENT_ID): str,
                        vol.Required(CONF_CLIENT_SECRET): str,
                    }
                )
            )
            return self.async_show_form(step_id=step, data_schema=schema, errors=errors)
        return await self.async_step_stream_cookie()

    async def async_step_stream_cookie(self, user_input=None) -> ConfigFlowResult:
        if user_input is not None:
            if user_input.get(CONF_STREAM_COOKIE):
                self._data[CONF_STREAM_COOKIE] = user_input[CONF_STREAM_COOKIE]
            self._data[CONF_ENTRY_SECRET] = secrets.token_hex(32)
            return self.async_create_entry(title="YouTube Music", data=self._data)
        return self.async_show_form(
            step_id="stream_cookie",
            data_schema=vol.Schema({vol.Optional(CONF_STREAM_COOKIE): str}),
        )

    # ---- Reauth ----
    async def async_step_reauth(self, entry_data) -> ConfigFlowResult:
        self._data = dict(entry_data)
        return await self.async_step_reauth_confirm()

    async def async_step_reauth_confirm(self, user_input=None) -> ConfigFlowResult:
        if self._data.get(CONF_AUTH_METHOD) == AUTH_OAUTH:
            return await self._reauth_oauth(user_input)
        return await self._reauth_cookie(user_input)

    async def _reauth_cookie(self, user_input=None) -> ConfigFlowResult:
        prompt = "Re-paste your browser Cookie header to re-authenticate."
        if user_input is not None:
            self._data[CONF_COOKIE] = user_input[CONF_COOKIE]
            try:
                await _validate(self.hass, self._data)
            except Exception:  # noqa: BLE001
                return self.async_show_form(
                    step_id="reauth_confirm",
                    data_schema=vol.Schema({vol.Required(CONF_COOKIE): str}),
                    description_placeholders={"prompt": prompt},
                    errors={"base": "auth_failed"},
                )
            return await self._reauth_finish()
        return self.async_show_form(
            step_id="reauth_confirm",
            data_schema=vol.Schema({vol.Required(CONF_COOKIE): str}),
            description_placeholders={"prompt": prompt},
        )

    async def _reauth_oauth(self, user_input=None) -> ConfigFlowResult:
        if self._creds is None:
            self._creds = OAuthCredentials(
                client_id=self._data[CONF_CLIENT_ID],
                client_secret=self._data[CONF_CLIENT_SECRET],
            )
        if user_input is not None and self._device_code is not None:
            try:
                token = await self.hass.async_add_executor_job(
                    self._creds.token_from_code, self._device_code
                )
                if "expires_at" not in token and "expires_in" in token:
                    token["expires_at"] = int(time.time()) + int(token["expires_in"])
                self._data[CONF_OAUTH_TOKEN] = token
                await _validate(self.hass, self._data)
            except Exception:  # noqa: BLE001
                return self.async_show_form(
                    step_id="reauth_confirm",
                    data_schema=vol.Schema({}),
                    description_placeholders={"prompt": self._oauth_prompt},
                    errors={"base": "oauth_pending"},
                )
            return await self._reauth_finish()
        code = await self.hass.async_add_executor_job(self._creds.get_code)
        self._device_code = code["device_code"]
        self._oauth_prompt = (
            f"Visit {code['verification_url']} and enter code: {code['user_code']}"
        )
        return self.async_show_form(
            step_id="reauth_confirm",
            data_schema=vol.Schema({}),
            description_placeholders={"prompt": self._oauth_prompt},
        )

    async def _reauth_finish(self) -> ConfigFlowResult:
        entry = self.hass.config_entries.async_get_entry(self.context["entry_id"])
        self.hass.config_entries.async_update_entry(entry, data=self._data)
        await self.hass.config_entries.async_reload(entry.entry_id)
        return self.async_abort(reason="reauth_successful")

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: ConfigEntry) -> OptionsFlow:
        return YtMusicOptionsFlow()


class YtMusicOptionsFlow(OptionsFlow):
    async def async_step_init(self, user_input=None) -> ConfigFlowResult:
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)
        opts = self.config_entry.options
        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Optional(
                        CONF_DEFAULT_SOURCE,
                        description={"suggested_value": opts.get(CONF_DEFAULT_SOURCE)},
                    ): selector.EntitySelector(
                        selector.EntitySelectorConfig(domain="media_player")
                    ),
                    vol.Optional(
                        CONF_RESULT_LIMIT,
                        default=opts.get(CONF_RESULT_LIMIT, DEFAULT_RESULT_LIMIT),
                    ): cv.positive_int,
                    vol.Optional(
                        CONF_AUTOPLAY,
                        default=opts.get(CONF_AUTOPLAY, DEFAULT_AUTOPLAY),
                    ): bool,
                }
            ),
        )
