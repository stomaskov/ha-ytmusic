"""youtubei request recipes for the TV backend: (endpoint, body) tuples."""

from __future__ import annotations

# TV ignores the search type filter; we send the "songs" params for one generic search.
_SEARCH_PARAMS = "EgWKAQIIAWoMEA4QChADEAQQCRAF"


def library_playlists_body() -> tuple[str, dict]:
    return "browse", {"browseId": "FEmusic_liked_playlists"}


def search_body(query: str) -> tuple[str, dict]:
    return "search", {"query": query, "params": _SEARCH_PARAMS}


def browse_body(browse_id: str) -> tuple[str, dict]:
    return "browse", {"browseId": browse_id}


def radio_body(video_id: str) -> tuple[str, dict]:
    return "next", {"videoId": video_id, "playlistId": f"RDAMVM{video_id}"}
