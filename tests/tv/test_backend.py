"""Tests for TvBackend: mocks TvClient.post and asserts correct return shapes."""

import json
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch


from custom_components.ytmusic.backend import SearchItem
from custom_components.ytmusic.models import Track

FIX = Path(__file__).parent.parent / "fixtures" / "tv"


def _load(name: str) -> dict:
    return json.loads((FIX / name).read_text())


# ---------------------------------------------------------------------------
# Existing test (Task 2) — must keep passing
# ---------------------------------------------------------------------------


def test_search_item_as_dict():
    s = SearchItem(
        kind="album",
        id="MPRE1",
        title="Discovery",
        subtitle="Daft Punk",
        thumbnail="http://t/a",
    )
    assert s.as_dict() == {
        "kind": "album",
        "id": "MPRE1",
        "title": "Discovery",
        "subtitle": "Daft Punk",
        "thumbnail": "http://t/a",
    }


# ---------------------------------------------------------------------------
# TvBackend tests (Task 7)
# ---------------------------------------------------------------------------


def _make_backend(hass):
    """Construct a TvBackend bypassing __init__ (no token needed for unit tests)."""
    from custom_components.ytmusic.tv.backend import TvBackend

    be = TvBackend.__new__(TvBackend)
    be._hass = hass
    be._client = AsyncMock()
    return be


async def test_tvbackend_search_returns_search_items(hass):
    be = _make_backend(hass)
    be._client.post.return_value = _load("search.json")
    out = await be.search("hello", "songs")
    assert isinstance(out, list)
    assert all(isinstance(i, SearchItem) for i in out)
    # fixture has song + artist
    kinds = {i.kind for i in out}
    assert "song" in kinds
    song = next(i for i in out if i.kind == "song")
    assert song.title == "Song One"
    assert song.id == "vid_song"


async def test_tvbackend_search_ignores_filter(hass):
    """TV search accepts a filter arg but ignores it (TV has no type filter)."""
    be = _make_backend(hass)
    be._client.post.return_value = _load("search.json")
    out_songs = await be.search("hello", "songs")
    out_albums = await be.search("hello", "albums")
    # same fixture → same count; filter has no effect
    assert len(out_songs) == len(out_albums)


async def test_tvbackend_library_returns_dicts(hass):
    be = _make_backend(hass)
    be._client.post.return_value = _load("library.json")
    out = await be.get_library_playlists()
    assert out and all({"id", "title", "thumbnail"} <= set(p) for p in out)
    assert out[0]["title"] == "Playlist One"


async def test_tvbackend_library_uses_correct_endpoint(hass):
    be = _make_backend(hass)
    be._client.post.return_value = _load("library.json")
    await be.get_library_playlists()
    be._client.post.assert_called_once_with(
        "browse", {"browseId": "FEmusic_liked_playlists"}
    )


async def test_tvbackend_playlist_tracks(hass):
    be = _make_backend(hass)
    be._client.post.return_value = _load("playlist_tracks.json")
    out = await be.get_playlist_tracks("PL1")
    assert out and isinstance(out[0], Track)
    assert out[0].video_id == "vid1"
    # VL prefix should be added
    be._client.post.assert_called_once()
    endpoint, body = be._client.post.call_args[0]
    assert body["browseId"].startswith("VL")


async def test_tvbackend_playlist_tracks_vl_not_doubled(hass):
    """If playlist_id already starts with VL, it must not be doubled."""
    be = _make_backend(hass)
    be._client.post.return_value = _load("playlist_tracks.json")
    await be.get_playlist_tracks("VLPL1")
    _, body = be._client.post.call_args[0]
    assert body["browseId"] == "VLPL1"


async def test_tvbackend_album_tracks(hass):
    be = _make_backend(hass)
    be._client.post.return_value = _load("album_tracks.json")
    out = await be.get_album_tracks("MPRE123")
    assert out and isinstance(out[0], Track)
    assert out[0].video_id == "vida1"


async def test_tvbackend_artist_songs(hass):
    be = _make_backend(hass)
    be._client.post.return_value = _load("playlist_tracks.json")
    out = await be.get_artist_songs("UCfake123")
    assert out and isinstance(out[0], Track)


async def test_tvbackend_radio(hass):
    be = _make_backend(hass)
    be._client.post.return_value = _load("radio.json")
    out = await be.get_radio("vidr1")
    assert out and isinstance(out[0], Track)
    assert out[0].video_id == "vidr1"


async def test_tvbackend_validate_calls_library(hass):
    be = _make_backend(hass)
    be._client.post.return_value = _load("library.json")
    await be.validate()
    be._client.post.assert_called_once()
    endpoint, body = be._client.post.call_args[0]
    assert endpoint == "browse"
    assert body.get("browseId") == "FEmusic_liked_playlists"


async def test_tv_capability_flags_are_false(hass):
    be = _make_backend(hass)
    assert be.typed_search is False
    assert be.lyrics_supported is False


async def test_tv_get_lyrics_returns_none(hass):
    be = _make_backend(hass)
    assert await be.get_lyrics("vid") is None


def test_tvbackend_init_tolerates_extra_token_keys(hass):
    """TvBackend.__init__ must not raise when the token dict has unknown Google keys."""
    from custom_components.ytmusic.tv.backend import TvBackend
    from ytmusicapi.auth.oauth import OAuthCredentials

    token_with_extras = {
        "access_token": "AT",
        "refresh_token": "RT",
        "scope": "https://www.googleapis.com/auth/youtube",
        "token_type": "Bearer",
        "expires_in": 3600,
        "expires_at": 9999999999,
        # extra key Google sometimes returns
        "refresh_token_expires_in": 7776000,
    }
    creds = MagicMock(spec=OAuthCredentials)
    # Patch RefreshingToken so we don't need a real network call
    with patch("custom_components.ytmusic.tv.backend.RefreshingToken") as mock_rt:
        mock_rt.return_value = MagicMock()
        be = TvBackend(hass, creds, token_with_extras)
    # RefreshingToken must be called WITHOUT the extra key
    call_kwargs = mock_rt.call_args.kwargs
    assert "refresh_token_expires_in" not in call_kwargs
    assert call_kwargs["access_token"] == "AT"
    assert be is not None
