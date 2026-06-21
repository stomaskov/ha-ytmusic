import pytest

from custom_components.ytmusic.auth import (
    build_browser_headers,
    make_sapisidhash,
    parse_cookie,
)
from custom_components.ytmusic.const import (
    AUTH_COOKIE,
    AUTH_OAUTH,
    CONF_AUTH_METHOD,
    CONF_CLIENT_ID,
    CONF_CLIENT_SECRET,
    CONF_COOKIE,
    CONF_OAUTH_TOKEN,
)

_COOKIE = "SAPISID=abc; __Secure-3PAPISID=def; __Secure-3PSID=ghi"


def test_parse_cookie():
    parsed = parse_cookie(_COOKIE)
    assert parsed["SAPISID"] == "abc"
    assert parsed["__Secure-3PAPISID"] == "def"


def test_make_sapisidhash_format():
    h = make_sapisidhash("def", now=1700000000)
    assert h.startswith("SAPISIDHASH 1700000000_")
    assert len(h.split("_")[1]) == 40  # sha1 hex
    import hashlib

    expected = hashlib.sha1(b"1700000000 def https://music.youtube.com").hexdigest()
    assert h == f"SAPISIDHASH 1700000000_{expected}"


def test_build_browser_headers_has_required_keys():
    headers = build_browser_headers(_COOKIE)
    assert headers["Cookie"] == _COOKIE
    assert "SAPISIDHASH" in headers["Authorization"]
    assert headers["X-Goog-AuthUser"] == "0"
    assert headers["origin"] == "https://music.youtube.com"
    assert "User-Agent" in headers


def test_build_browser_headers_rejects_incomplete_cookie():
    with pytest.raises(ValueError):
        build_browser_headers("foo=bar")


def test_build_client_oauth():
    from unittest.mock import patch
    from custom_components.ytmusic.auth import build_client

    data = {
        CONF_AUTH_METHOD: AUTH_OAUTH,
        CONF_CLIENT_ID: "cid",
        CONF_CLIENT_SECRET: "csec",
        CONF_OAUTH_TOKEN: {"access_token": "AT"},
    }
    with (
        patch("custom_components.ytmusic.auth.YTMusic") as ytm,
        patch("custom_components.ytmusic.auth.OAuthCredentials") as oc,
    ):
        client = build_client(data)
    oc.assert_called_once_with(client_id="cid", client_secret="csec")
    ytm.assert_called_once_with(
        auth={"access_token": "AT"}, oauth_credentials=oc.return_value
    )
    assert client is ytm.return_value


def test_build_client_cookie():
    from unittest.mock import patch
    from custom_components.ytmusic.auth import build_client

    data = {CONF_AUTH_METHOD: AUTH_COOKIE, CONF_COOKIE: _COOKIE}
    with patch("custom_components.ytmusic.auth.YTMusic") as ytm:
        client = build_client(data)
    _args, kwargs = ytm.call_args
    headers = kwargs.get("auth") if "auth" in kwargs else _args[0]
    assert "SAPISIDHASH" in headers["Authorization"]
    assert headers["Cookie"] == _COOKIE
    assert client is ytm.return_value
