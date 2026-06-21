"""HMAC-signed stream proxy endpoint."""

from __future__ import annotations

import hashlib
import hmac
import logging

from aiohttp import web

from homeassistant.components.http import HomeAssistantView

from .const import STREAM_URL_BASE
from .stream import StreamResolver

_LOGGER = logging.getLogger(__name__)


def sign(secret: str, entry_id: str, video_id: str) -> str:
    msg = f"{entry_id}:{video_id}".encode()
    return hmac.new(secret.encode(), msg, hashlib.sha256).hexdigest()


def build_stream_path(entry_id: str, video_id: str, secret: str) -> str:
    return f"{STREAM_URL_BASE}/{entry_id}/{video_id}/{sign(secret, entry_id, video_id)}"


class YtMusicStreamView(HomeAssistantView):
    url = STREAM_URL_BASE + "/{entry_id}/{video_id}/{signature}"
    name = "api:ytmusic:stream"
    requires_auth = False

    def __init__(
        self,
        resolvers: dict[str, StreamResolver],
        secrets: dict[str, str],
    ) -> None:
        self._resolvers = resolvers
        self._secrets = secrets

    async def get(self, request, entry_id: str, video_id: str, signature: str):
        secret = self._secrets.get(entry_id)
        resolver = self._resolvers.get(entry_id)
        if secret is None or resolver is None:
            return web.Response(status=404)
        if not hmac.compare_digest(signature, sign(secret, entry_id, video_id)):
            return web.Response(status=403)
        try:
            url = await resolver.resolve(video_id)
        except Exception as err:  # noqa: BLE001
            _LOGGER.error("Stream resolve failed for %s: %s", video_id, err)
            return web.Response(status=502)
        return web.Response(status=302, headers={"Location": url})
