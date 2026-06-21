from unittest.mock import MagicMock

from custom_components.ytmusic.api import YtMusicApi
from custom_components.ytmusic.backend import SearchItem
from custom_components.ytmusic.models import LyricLine, LyricsResult


def test_lyrics_models_as_dict():
    res = LyricsResult(
        lines=[LyricLine("hello", 0), LyricLine("world", 1500)], synced=True
    )
    assert res.as_dict() == {
        "lines": [
            {"text": "hello", "start_ms": 0},
            {"text": "world", "start_ms": 1500},
        ],
        "synced": True,
    }


def _api(hass, client):
    return YtMusicApi(hass, client)


async def test_api_capability_flags(hass):
    api = _api(hass, MagicMock())
    assert api.typed_search is True
    assert api.lyrics_supported is True


async def test_get_lyrics_synced(hass):
    client = MagicMock()
    client.get_watch_playlist.return_value = {"lyrics": "MPLYt_browseid"}
    client.get_lyrics.return_value = {
        "lyrics": [
            {"text": "line one", "start_time": 0},
            {"text": "line two", "start_time": 2000},
        ]
    }
    api = _api(hass, client)
    res = await api.get_lyrics("vid")
    assert res.synced is True
    assert [ln.text for ln in res.lines] == ["line one", "line two"]
    assert res.lines[1].start_ms == 2000


async def test_get_lyrics_unsynced_string(hass):
    client = MagicMock()
    client.get_watch_playlist.return_value = {"lyrics": "MPLYt_browseid"}
    client.get_lyrics.return_value = {"lyrics": "first\n\nsecond"}
    api = _api(hass, client)
    res = await api.get_lyrics("vid")
    assert res.synced is False
    assert [ln.text for ln in res.lines] == ["first", "second"]
    assert res.lines[0].start_ms is None


async def test_get_lyrics_none_when_absent(hass):
    client = MagicMock()
    client.get_watch_playlist.return_value = {"lyrics": None}
    api = _api(hass, client)
    assert await api.get_lyrics("vid") is None


async def test_get_lyrics_timestamps_fallback(hass):
    client = MagicMock()
    client.get_watch_playlist.return_value = {"lyrics": "MPLYt_browseid"}
    client.get_lyrics.side_effect = [TypeError("unexpected arg"), {"lyrics": "plain"}]
    api = _api(hass, client)
    res = await api.get_lyrics("vid")
    assert res is not None
    assert res.synced is False
    assert [ln.text for ln in res.lines] == ["plain"]


_SONG = {
    "videoId": "v1",
    "title": "Song One",
    "artists": [{"name": "Artist A"}],
    "album": {"name": "Album X"},
    "duration_seconds": 200,
    "thumbnails": [{"url": "http://t/small"}, {"url": "http://t/big"}],
}

_ALBUM = {
    "browseId": "MPREb_abc123",
    "title": "Discovery",
    "artists": [{"name": "Daft Punk"}],
    "thumbnails": [{"url": "http://t/album"}],
}


async def test_search_returns_search_items(hass):
    client = MagicMock()
    client.search.return_value = [_SONG]
    api = YtMusicApi(hass, client)
    results = await api.search("hello", "songs")
    assert results == [
        SearchItem(
            kind="song",
            id="v1",
            title="Song One",
            subtitle="Artist A",
            thumbnail="http://t/big",
        )
    ]
    client.search.assert_called_once_with("hello", filter="songs")


async def test_search_includes_albums_without_video_id(hass):
    """Albums have browseId but no videoId — they must be kept, not dropped."""
    client = MagicMock()
    client.search.return_value = [_SONG, _ALBUM]
    api = YtMusicApi(hass, client)
    results = await api.search("daft punk", "albums")
    assert len(results) == 2
    album = next(r for r in results if r.kind == "album")
    assert album.id == "MPREb_abc123"
    assert album.title == "Discovery"
    assert album.subtitle == "Daft Punk"


async def test_search_drops_items_with_neither_id(hass):
    """Items with no videoId and no browseId are silently dropped."""
    client = MagicMock()
    client.search.return_value = [{"title": "Ghost", "artists": []}]
    api = YtMusicApi(hass, client)
    results = await api.search("ghost", "songs")
    assert results == []


async def test_get_library_playlists(hass):
    client = MagicMock()
    client.get_library_playlists.return_value = [
        {"playlistId": "PL1", "title": "Mix", "thumbnails": [{"url": "http://t/a"}]}
    ]
    api = YtMusicApi(hass, client)
    out = await api.get_library_playlists()
    assert out == [{"id": "PL1", "title": "Mix", "thumbnail": "http://t/a"}]


async def test_get_radio_uses_watch_playlist(hass):
    client = MagicMock()
    client.get_watch_playlist.return_value = {"tracks": [_SONG]}
    api = YtMusicApi(hass, client)
    out = await api.get_radio("v1")
    assert out[0].video_id == "v1"
    client.get_watch_playlist.assert_called_once_with(videoId="v1", radio=True)


async def test_get_playlist_tracks(hass):
    client = MagicMock()
    client.get_playlist.return_value = {"tracks": [_SONG]}
    api = YtMusicApi(hass, client)
    tracks = await api.get_playlist_tracks("PL1")
    assert tracks[0].video_id == "v1"
    assert tracks[0].album == "Album X"
    client.get_playlist.assert_called_once_with("PL1")


async def test_get_album_tracks(hass):
    client = MagicMock()
    client.get_album.return_value = {"tracks": [_SONG]}
    api = YtMusicApi(hass, client)
    tracks = await api.get_album_tracks("MPRE123")
    assert tracks[0].video_id == "v1"
    client.get_album.assert_called_once_with("MPRE123")


async def test_get_artist_songs(hass):
    client = MagicMock()
    client.get_artist.return_value = {"songs": {"results": [_SONG]}}
    api = YtMusicApi(hass, client)
    tracks = await api.get_artist_songs("UC123")
    assert tracks[0].video_id == "v1"
    assert tracks[0].artists == "Artist A"
    client.get_artist.assert_called_once_with("UC123")


async def test_to_track_tolerates_missing_optional_fields(hass):
    client = MagicMock()
    # a track with NO artists/album/thumbnails must parse without raising
    client.get_playlist.return_value = {"tracks": [{"videoId": "x", "title": "T"}]}
    api = YtMusicApi(hass, client)
    tracks = await api.get_playlist_tracks("PL")
    assert tracks[0].artists == ""
    assert tracks[0].album is None
    assert tracks[0].thumbnail is None


async def test_search_uc_browse_id_returns_artist(hass):
    """A search result with a browseId starting UC and no videoId → kind='artist'."""
    uc_artist = {
        "browseId": "UCxkefR5x8ZuE-SHQA0BPQWQ",
        "title": "Some Artist",
        "artists": [{"name": "Some Artist"}],
        "thumbnails": [{"url": "http://t/artist"}],
    }
    client = MagicMock()
    client.search.return_value = [uc_artist]
    api = YtMusicApi(hass, client)
    results = await api.search("Some Artist", "artists")
    assert len(results) == 1
    item = results[0]
    assert item.kind == "artist"
    assert item.id == "UCxkefR5x8ZuE-SHQA0BPQWQ"
