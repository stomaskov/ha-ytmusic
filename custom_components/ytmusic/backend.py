"""Backend contract shared by the cookie (ytmusicapi) and OAuth (TV) backends."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from .models import LyricsResult, Track


@dataclass(frozen=True, slots=True)
class SearchItem:
    kind: str  # song | video | playlist | album | artist
    id: str  # videoId (song/video) or browseId (playlist/album/artist)
    title: str
    subtitle: str = ""
    thumbnail: str | None = None

    def as_dict(self) -> dict:
        return {
            "kind": self.kind,
            "id": self.id,
            "title": self.title,
            "subtitle": self.subtitle,
            "thumbnail": self.thumbnail,
        }


class MusicBackend(Protocol):
    typed_search: bool
    lyrics_supported: bool

    async def validate(self) -> None: ...
    async def search(self, query: str, filter: str) -> list[SearchItem]: ...
    async def get_library_playlists(self) -> list[dict]: ...
    async def get_playlist_tracks(self, playlist_id: str) -> list[Track]: ...
    async def get_album_tracks(self, browse_id: str) -> list[Track]: ...
    async def get_artist_songs(self, channel_id: str) -> list[Track]: ...
    async def get_radio(self, video_id: str) -> list[Track]: ...
    async def get_lyrics(self, video_id: str) -> LyricsResult | None: ...
