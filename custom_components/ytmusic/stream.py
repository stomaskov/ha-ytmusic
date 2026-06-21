"""yt-dlp stream-URL resolution with a short TTL cache."""

from __future__ import annotations

import logging
import time
from collections.abc import Callable

from yt_dlp import YoutubeDL

from homeassistant.core import HomeAssistant

from .const import STREAM_CACHE_TTL, STREAM_FORMAT

_LOGGER = logging.getLogger(__name__)
_FALLBACK_FORMAT = "bestaudio/best"
_WATCH_URL = "https://music.youtube.com/watch?v={vid}"


class StreamResolver:
    def __init__(
        self,
        hass: HomeAssistant,
        cookiefile: str | None = None,
        ttl: int = STREAM_CACHE_TTL,
        time_fn: Callable[[], float] = time.monotonic,
    ) -> None:
        self._hass = hass
        self._cookiefile = cookiefile
        self._ttl = ttl
        self._time = time_fn
        self._cache: dict[str, tuple[str, float]] = {}

    async def resolve(self, video_id: str) -> str:
        cached = self._cache.get(video_id)
        if cached and cached[1] > self._time():
            return cached[0]
        try:
            url = await self._hass.async_add_executor_job(
                self._extract, video_id, STREAM_FORMAT
            )
        except Exception as err:  # noqa: BLE001 - retry once with a looser format
            _LOGGER.warning("yt-dlp primary extract failed for %s: %s", video_id, err)
            try:
                url = await self._hass.async_add_executor_job(
                    self._extract, video_id, _FALLBACK_FORMAT
                )
            except Exception as err2:  # noqa: BLE001
                raise RuntimeError(
                    f"Could not resolve stream for {video_id}: {err2}"
                ) from err2
        self._cache[video_id] = (url, self._time() + self._ttl)
        return url

    def _extract(self, video_id: str, fmt: str) -> str:
        opts: dict = {
            "format": fmt,
            "quiet": True,
            "no_warnings": True,
            "noplaylist": True,
            "skip_download": True,
        }
        if self._cookiefile:
            opts["cookiefile"] = self._cookiefile
        with YoutubeDL(opts) as ydl:
            info = ydl.extract_info(_WATCH_URL.format(vid=video_id), download=False)
        url = info.get("url")
        if not url:
            raise RuntimeError("yt-dlp returned no stream url")
        return url
