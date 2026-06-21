"""Library data coordinator."""

from __future__ import annotations

from datetime import timedelta
import logging

from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import YtMusicApi
from .tv.errors import TvAuthError, TvFormatError

_LOGGER = logging.getLogger(__name__)


class YtMusicCoordinator(DataUpdateCoordinator[list[dict]]):
    def __init__(self, hass: HomeAssistant, api: YtMusicApi) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name="ytmusic library",
            update_interval=timedelta(minutes=30),
        )
        self._api = api

    async def _async_update_data(self) -> list[dict]:
        try:
            return await self._api.get_library_playlists()
        except TvFormatError:
            # Let TvFormatError propagate unwrapped so the HA coordinator stores
            # it verbatim in last_exception; __init__.py inspects it to register
            # a Repairs issue before re-raising ConfigEntryNotReady.
            raise
        except TvAuthError as err:
            raise ConfigEntryAuthFailed(str(err)) from err
        except Exception as err:  # noqa: BLE001
            raise UpdateFailed(str(err)) from err
