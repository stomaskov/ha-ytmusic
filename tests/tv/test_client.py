from unittest.mock import MagicMock, patch

import pytest

from custom_components.ytmusic.tv.client import TvClient
from custom_components.ytmusic.tv.errors import TvAuthError, TvTransientError


def _resp(status, json_body=None, text="{}"):
    r = MagicMock()
    r.status_code = status
    r.json.return_value = json_body if json_body is not None else {}
    r.text = text
    return r


async def test_post_sends_tvhtml5_context_and_bearer(hass):
    client = TvClient(hass, token_provider=lambda: "AT123")
    with patch("custom_components.ytmusic.tv.client.requests.post") as post:
        post.return_value = _resp(200, {"contents": {}})
        await client.post("browse", {"browseId": "FEmusic_liked_playlists"})
    sent = post.call_args
    body = sent.kwargs["json"]
    assert body["context"]["client"]["clientName"] == "TVHTML5"
    assert body["browseId"] == "FEmusic_liked_playlists"
    assert sent.kwargs["headers"]["Authorization"] == "Bearer AT123"


async def test_post_401_raises_auth(hass):
    client = TvClient(hass, token_provider=lambda: "AT")
    with patch(
        "custom_components.ytmusic.tv.client.requests.post", return_value=_resp(401)
    ):
        with pytest.raises(TvAuthError):
            await client.post("browse", {})


async def test_post_500_raises_transient(hass):
    client = TvClient(hass, token_provider=lambda: "AT")
    with patch(
        "custom_components.ytmusic.tv.client.requests.post", return_value=_resp(503)
    ):
        with pytest.raises(TvTransientError):
            await client.post("browse", {})


async def test_post_returns_json(hass):
    client = TvClient(hass, token_provider=lambda: "AT")
    with patch(
        "custom_components.ytmusic.tv.client.requests.post",
        return_value=_resp(200, {"contents": {"ok": 1}}),
    ):
        out = await client.post("browse", {})
    assert out == {"contents": {"ok": 1}}
