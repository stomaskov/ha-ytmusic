"""OAuth backend: youtubei TV client + parsers, conforming to MusicBackend."""

from __future__ import annotations

from homeassistant.core import HomeAssistant
from ytmusicapi.auth.oauth import OAuthCredentials, RefreshingToken
from ytmusicapi.auth.oauth.token import OAuthToken

from ..backend import SearchItem
from ..models import Track
from . import endpoints, parse
from .client import TvClient


class TvBackend:
    typed_search = False
    lyrics_supported = False

    def __init__(
        self,
        hass: HomeAssistant,
        credentials: OAuthCredentials,
        token: dict,
    ) -> None:
        self._hass = hass
        known = {k: v for k, v in token.items() if k in OAuthToken.members()}
        self._token = RefreshingToken(credentials=credentials, **known)
        self._client = TvClient(hass, token_provider=lambda: self._token.access_token)

    async def validate(self) -> None:
        await self.get_library_playlists()

    async def search(self, query: str, filter: str) -> list[SearchItem]:  # noqa: A002
        # TV search has no type filter; the filter arg is accepted but ignored.
        return parse.parse_search(
            await self._client.post(*endpoints.search_body(query))
        )

    async def get_library_playlists(self) -> list[dict]:
        return parse.parse_library_playlists(
            await self._client.post(*endpoints.library_playlists_body())
        )

    async def get_playlist_tracks(self, playlist_id: str) -> list[Track]:
        bid = playlist_id if playlist_id.startswith("VL") else f"VL{playlist_id}"
        return parse.parse_tracks(await self._client.post(*endpoints.browse_body(bid)))

    async def get_album_tracks(self, browse_id: str) -> list[Track]:
        return parse.parse_tracks(
            await self._client.post(*endpoints.browse_body(browse_id))
        )

    async def get_artist_songs(self, channel_id: str) -> list[Track]:
        return parse.parse_tracks(
            await self._client.post(*endpoints.browse_body(channel_id))
        )

    async def get_radio(self, video_id: str) -> list[Track]:
        return parse.parse_radio(
            await self._client.post(*endpoints.radio_body(video_id))
        )

    async def get_lyrics(self, video_id: str) -> None:
        # TV (youtubei) lyrics are not implemented in v1; OAuth advertises
        # lyrics_supported=False so the card hides the toggle.
        return None
