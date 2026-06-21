from unittest.mock import AsyncMock, MagicMock, patch


from homeassistant.config_entries import ConfigEntryState
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components import ytmusic
from custom_components.ytmusic.const import (
    AUTH_COOKIE,
    AUTH_OAUTH,
    CONF_AUTH_METHOD,
    CONF_CLIENT_ID,
    CONF_CLIENT_SECRET,
    CONF_COOKIE,
    CONF_ENTRY_SECRET,
    CONF_OAUTH_TOKEN,
    DOMAIN,
)

_COOKIE = "SAPISID=abc; __Secure-3PAPISID=def; __Secure-3PSID=ghi"


def _entry():
    return MockConfigEntry(
        domain=DOMAIN,
        data={
            CONF_AUTH_METHOD: AUTH_COOKIE,
            CONF_COOKIE: _COOKIE,
            CONF_ENTRY_SECRET: "deadbeef",
        },
        options={},
    )


async def test_setup_and_unload(hass):
    entry = _entry()
    entry.add_to_hass(hass)
    fake_api = AsyncMock()
    fake_api.get_library_playlists.return_value = []
    with (
        patch("custom_components.ytmusic.build_client", return_value=MagicMock()),
        patch("custom_components.ytmusic.YtMusicApi", return_value=fake_api),
        patch("custom_components.ytmusic.add_extra_js_url"),
    ):
        assert await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()
    assert entry.state is ConfigEntryState.LOADED
    assert entry.runtime_data.entry_secret == "deadbeef"
    assert entry.entry_id in ytmusic.STREAM_RESOLVERS
    assert entry.entry_id in ytmusic.STREAM_SECRETS

    assert await hass.config_entries.async_unload(entry.entry_id)
    await hass.async_block_till_done()
    assert entry.state is ConfigEntryState.NOT_LOADED
    assert entry.entry_id not in ytmusic.STREAM_RESOLVERS
    assert entry.entry_id not in ytmusic.STREAM_SECRETS


async def test_setup_data_failure_retries(hass):
    entry = _entry()
    entry.add_to_hass(hass)
    fake_api = AsyncMock()
    fake_api.get_library_playlists.side_effect = Exception("401")
    with (
        patch("custom_components.ytmusic.build_client", return_value=MagicMock()),
        patch("custom_components.ytmusic.YtMusicApi", return_value=fake_api),
    ):
        assert not await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()
    assert entry.state is ConfigEntryState.SETUP_RETRY


async def test_setup_bad_credentials_auth_failed(hass):
    entry = _entry()
    entry.add_to_hass(hass)
    with patch(
        "custom_components.ytmusic.build_client", side_effect=ValueError("bad cookie")
    ):
        assert not await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()
    assert entry.state is ConfigEntryState.SETUP_ERROR


_OAUTH_TOKEN = {
    "access_token": "a",
    "refresh_token": "r",
    "scope": "x",
    "token_type": "Bearer",
    "expires_in": 3600,
    "expires_at": 9999999999,
}


async def test_setup_oauth_uses_tv_backend(hass):
    """OAuth entry must use TvBackend, never the cookie YtMusicApi."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        data={
            CONF_AUTH_METHOD: AUTH_OAUTH,
            CONF_CLIENT_ID: "c",
            CONF_CLIENT_SECRET: "s",
            CONF_OAUTH_TOKEN: _OAUTH_TOKEN,
            CONF_ENTRY_SECRET: "deadbeef",
        },
        options={},
    )
    entry.add_to_hass(hass)
    fake = AsyncMock()
    fake.get_library_playlists.return_value = []
    with (
        patch("custom_components.ytmusic.TvBackend", return_value=fake) as mock_tv,
        patch("custom_components.ytmusic.YtMusicApi") as mock_cookie,
        patch("custom_components.ytmusic.add_extra_js_url"),
    ):
        assert await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()
    mock_cookie.assert_not_called()
    mock_tv.assert_called_once()
    assert entry.state is ConfigEntryState.LOADED


async def test_setup_oauth_tv_auth_error_triggers_reauth(hass):
    """TvAuthError during first refresh must trigger reauth, not SETUP_RETRY."""
    from custom_components.ytmusic.tv.errors import TvAuthError

    entry = MockConfigEntry(
        domain=DOMAIN,
        data={
            CONF_AUTH_METHOD: AUTH_OAUTH,
            CONF_CLIENT_ID: "c",
            CONF_CLIENT_SECRET: "s",
            CONF_OAUTH_TOKEN: _OAUTH_TOKEN,
            CONF_ENTRY_SECRET: "deadbeef",
        },
        options={},
    )
    entry.add_to_hass(hass)
    fake = AsyncMock()
    fake.get_library_playlists.side_effect = TvAuthError(
        "oauth refresh rejected: bad client"
    )
    # Patch get_code so the auto-started reauth flow doesn't make real network calls
    with (
        patch("custom_components.ytmusic.TvBackend", return_value=fake),
        patch(
            "ytmusicapi.auth.oauth.credentials.OAuthCredentials.get_code",
            return_value={
                "device_code": "dc",
                "verification_url": "https://example.com",
                "user_code": "ABC-123",
            },
        ),
    ):
        assert not await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()
    # ConfigEntryAuthFailed puts entry in SETUP_ERROR and starts a reauth flow
    assert entry.state is ConfigEntryState.SETUP_ERROR
    flows = hass.config_entries.flow.async_progress()
    assert any(f["context"].get("source") == "reauth" for f in flows)


async def test_card_url_is_versioned(hass):
    """add_extra_js_url must include a ?v= cache-buster when the bundle exists."""
    import custom_components.ytmusic as ytm

    captured_urls: list[str] = []

    hass.data.pop(ytm._CARD_REGISTERED, None)

    mock_http = MagicMock()
    mock_http.async_register_static_paths = AsyncMock()

    with (
        patch.object(ytm, "add_extra_js_url", side_effect=lambda h, u: captured_urls.append(u)),
        patch("custom_components.ytmusic.os.path.exists", return_value=True),
        patch.object(hass, "async_add_executor_job", new=AsyncMock(return_value=True)),
        patch.object(hass, "http", mock_http, create=True),
    ):
        await ytm._register_card_once(hass)

    assert captured_urls, "add_extra_js_url was never called"
    assert captured_urls[0] == f"{ytm._CARD_URL}?v={ytm._CARD_VERSION}"
    assert "?v=" in captured_urls[0]


async def test_setup_tv_format_error_creates_repair(hass):
    """TvFormatError during first refresh must create a Repairs issue + SETUP_RETRY."""
    from custom_components.ytmusic.tv.errors import TvFormatError

    entry = MockConfigEntry(
        domain=DOMAIN,
        data={
            CONF_AUTH_METHOD: AUTH_OAUTH,
            CONF_CLIENT_ID: "c",
            CONF_CLIENT_SECRET: "s",
            CONF_OAUTH_TOKEN: _OAUTH_TOKEN,
            CONF_ENTRY_SECRET: "deadbeef",
        },
        options={},
    )
    entry.add_to_hass(hass)
    fake = AsyncMock()
    fake.get_library_playlists.side_effect = TvFormatError("unexpected shape")
    with (
        patch("custom_components.ytmusic.TvBackend", return_value=fake),
        patch("custom_components.ytmusic.ir") as mock_ir,
    ):
        assert not await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()
    mock_ir.async_create_issue.assert_called_once()
    assert entry.state is ConfigEntryState.SETUP_RETRY
