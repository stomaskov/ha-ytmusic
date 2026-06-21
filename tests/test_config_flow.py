from unittest.mock import AsyncMock, MagicMock, patch


from homeassistant import config_entries, data_entry_flow
from pytest_homeassistant_custom_component.common import MockConfigEntry

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


def _patch_validate(ok=True):
    """Patch the API validation call used after auth."""
    api = AsyncMock()
    if ok:
        api.get_library_playlists.return_value = [
            {"id": "PL1", "title": "x", "thumbnail": None}
        ]
    else:
        api.get_library_playlists.side_effect = Exception("auth failed")
    return api


async def test_user_step_menu(hass):
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    assert result["type"] == data_entry_flow.FlowResultType.MENU
    assert set(result["menu_options"]) == {AUTH_OAUTH, AUTH_COOKIE}


async def test_cookie_path_creates_entry(hass):
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {"next_step_id": AUTH_COOKIE}
    )
    with (
        patch(
            "custom_components.ytmusic.config_flow.build_client",
            return_value=MagicMock(),
        ),
        patch(
            "custom_components.ytmusic.config_flow.YtMusicApi",
            return_value=_patch_validate(ok=True),
        ),
    ):
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"], {CONF_COOKIE: _COOKIE}
        )
        # optional stream-cookie step -> submit empty to skip
        result = await hass.config_entries.flow.async_configure(result["flow_id"], {})
    assert result["type"] == data_entry_flow.FlowResultType.CREATE_ENTRY
    data = result["data"]
    assert data[CONF_AUTH_METHOD] == AUTH_COOKIE
    assert data[CONF_COOKIE] == _COOKIE
    assert CONF_ENTRY_SECRET in data  # secret generated


async def test_cookie_path_invalid_auth_shows_error(hass):
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {"next_step_id": AUTH_COOKIE}
    )
    with (
        patch(
            "custom_components.ytmusic.config_flow.build_client",
            return_value=MagicMock(),
        ),
        patch(
            "custom_components.ytmusic.config_flow.YtMusicApi",
            return_value=_patch_validate(ok=False),
        ),
    ):
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"], {CONF_COOKIE: _COOKIE}
        )
    assert result["type"] == data_entry_flow.FlowResultType.FORM
    assert result["errors"]["base"] == "auth_failed"


async def test_oauth_path_creates_entry(hass):
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {"next_step_id": AUTH_OAUTH}
    )
    fake_creds = MagicMock()
    fake_creds.get_code.return_value = {
        "device_code": "DC",
        "user_code": "ABC-DEF",
        "verification_url": "https://google.com/device",
        "interval": 5,
        "expires_in": 1800,
    }
    fake_creds.token_from_code.return_value = {
        "access_token": "AT",
        "refresh_token": "RT",
    }
    with patch(
        "custom_components.ytmusic.config_flow.OAuthCredentials",
        return_value=fake_creds,
    ):
        # submit client creds -> shows device code form
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {CONF_CLIENT_ID: "cid", CONF_CLIENT_SECRET: "csec"},
        )
        assert result["step_id"] == "oauth_device"
        # user authorized -> resubmit to exchange. OAuth validates via the TV backend.
        with patch("custom_components.ytmusic.tv.backend.TvBackend") as tv:
            tv.return_value.validate = AsyncMock()
            result = await hass.config_entries.flow.async_configure(
                result["flow_id"], {}
            )
            result = await hass.config_entries.flow.async_configure(
                result["flow_id"], {}
            )  # skip stream cookie
    assert result["type"] == data_entry_flow.FlowResultType.CREATE_ENTRY
    assert result["data"][CONF_AUTH_METHOD] == AUTH_OAUTH
    assert result["data"][CONF_OAUTH_TOKEN] == {
        "access_token": "AT",
        "refresh_token": "RT",
    }


async def test_reauth_cookie_updates_entry(hass):
    entry = MockConfigEntry(
        domain=DOMAIN,
        data={
            CONF_AUTH_METHOD: AUTH_COOKIE,
            CONF_COOKIE: "stale",
            CONF_ENTRY_SECRET: "s",
        },
    )
    entry.add_to_hass(hass)
    result = await hass.config_entries.flow.async_init(
        DOMAIN,
        context={"source": config_entries.SOURCE_REAUTH, "entry_id": entry.entry_id},
        data=dict(entry.data),
    )
    assert result["step_id"] == "reauth_confirm"
    with (
        patch(
            "custom_components.ytmusic.config_flow.build_client",
            return_value=MagicMock(),
        ),
        patch(
            "custom_components.ytmusic.config_flow.YtMusicApi",
            return_value=_patch_validate(ok=True),
        ),
        patch.object(
            hass.config_entries, "async_reload", new=AsyncMock(return_value=True)
        ),
    ):
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"], {CONF_COOKIE: _COOKIE}
        )
    assert result["type"] == data_entry_flow.FlowResultType.ABORT
    assert result["reason"] == "reauth_successful"
    assert entry.data[CONF_COOKIE] == _COOKIE


async def test_reauth_oauth_updates_token(hass):
    entry = MockConfigEntry(
        domain=DOMAIN,
        data={
            CONF_AUTH_METHOD: AUTH_OAUTH,
            CONF_CLIENT_ID: "cid",
            CONF_CLIENT_SECRET: "csec",
            CONF_OAUTH_TOKEN: {"access_token": "OLD"},
            CONF_ENTRY_SECRET: "s",
        },
    )
    entry.add_to_hass(hass)
    fake_creds = MagicMock()
    fake_creds.get_code.return_value = {
        "device_code": "DC",
        "user_code": "ABC-DEF",
        "verification_url": "https://google.com/device",
        "interval": 5,
        "expires_in": 1800,
    }
    fake_creds.token_from_code.return_value = {
        "access_token": "NEW",
        "refresh_token": "RT",
    }
    with patch(
        "custom_components.ytmusic.config_flow.OAuthCredentials",
        return_value=fake_creds,
    ):
        result = await hass.config_entries.flow.async_init(
            DOMAIN,
            context={
                "source": config_entries.SOURCE_REAUTH,
                "entry_id": entry.entry_id,
            },
            data=dict(entry.data),
        )
        assert result["step_id"] == "reauth_confirm"  # device prompt shown
        with (
            patch("custom_components.ytmusic.tv.backend.TvBackend") as tv,
            patch.object(
                hass.config_entries, "async_reload", new=AsyncMock(return_value=True)
            ),
        ):
            tv.return_value.validate = AsyncMock()
            result = await hass.config_entries.flow.async_configure(
                result["flow_id"], {}
            )
    assert result["type"] == data_entry_flow.FlowResultType.ABORT
    assert result["reason"] == "reauth_successful"
    assert entry.data[CONF_OAUTH_TOKEN] == {
        "access_token": "NEW",
        "refresh_token": "RT",
    }
