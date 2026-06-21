"""Thin youtubei client for the OAuth path: TVHTML5 context + Bearer token."""

from __future__ import annotations

import time
from collections.abc import Callable

import requests
from ytmusicapi.auth.oauth.exceptions import BadOAuthClient, UnauthorizedOAuthClient

from homeassistant.core import HomeAssistant

from ..const import TV_BASE_API, TV_CLIENT_NAME, TV_CLIENT_VERSION
from .errors import TvAuthError, TvFormatError, TvTransientError

_UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:88.0) Gecko/20100101 Firefox/88.0"
_TIMEOUT = 30


class TvClient:
    def __init__(
        self,
        hass: HomeAssistant,
        token_provider: Callable[[], str],
        gl: str = "US",
        hl: str = "en",
    ) -> None:
        self._hass = hass
        self._token = token_provider
        self._gl = gl
        self._hl = hl

    async def post(self, endpoint: str, body: dict) -> dict:
        return await self._hass.async_add_executor_job(self._post, endpoint, body)

    def _post(self, endpoint: str, body: dict) -> dict:
        try:
            bearer = self._token()
        except (BadOAuthClient, UnauthorizedOAuthClient) as err:
            raise TvAuthError(f"oauth refresh rejected: {err}") from err
        payload = dict(body)
        payload["context"] = {
            "client": {
                "clientName": TV_CLIENT_NAME,
                "clientVersion": TV_CLIENT_VERSION,
                "hl": self._hl,
                "gl": self._gl,
            },
            "user": {},
        }
        headers = {
            "Authorization": f"Bearer {bearer}",
            "Content-Type": "application/json",
            "X-Goog-Request-Time": str(int(time.time())),
            "User-Agent": _UA,
        }
        try:
            resp = requests.post(
                TV_BASE_API + endpoint + "?prettyPrint=false",
                json=payload,
                headers=headers,
                timeout=_TIMEOUT,
            )
        except requests.RequestException as err:
            raise TvTransientError(str(err)) from err
        if resp.status_code in (401, 403):
            raise TvAuthError(f"HTTP {resp.status_code}")
        if resp.status_code >= 500:
            raise TvTransientError(f"HTTP {resp.status_code}")
        try:
            data = resp.json()
        except ValueError as err:
            raise TvFormatError("non-JSON response") from err
        if resp.status_code >= 400:
            raise TvFormatError(f"HTTP {resp.status_code}: {list(data.keys())}")
        return data
