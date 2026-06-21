import json
from pathlib import Path

import pytest

from custom_components.ytmusic.tv.errors import TvFormatError
from custom_components.ytmusic.tv.parse import (
    parse_library_playlists,
    parse_radio,
    parse_search,
    parse_tracks,
)

FIX = Path(__file__).parent.parent / "fixtures" / "tv"


def _load(name):
    return json.loads((FIX / name).read_text())


def test_parse_search_mixed_kinds():
    out = parse_search(_load("search.json"))
    assert len(out) == 2
    kinds = {i.kind for i in out}
    assert "song" in kinds and "artist" in kinds
    song = next(i for i in out if i.kind == "song")
    assert (
        song.id == "vid_song"
        and song.title == "Song One"
        and song.subtitle == "Artist A"
    )
    artist = next(i for i in out if i.kind == "artist")
    assert artist.id.startswith("UC")


def test_parse_library_playlists():
    out = parse_library_playlists(_load("library.json"))
    assert len(out) == 2
    assert all({"id", "title", "thumbnail"} <= set(p) for p in out)
    assert out[0]["title"] == "Playlist One"
    assert out[0]["id"].startswith("VL")


def test_parse_playlist_tracks():
    out = parse_tracks(_load("playlist_tracks.json"))
    assert len(out) == 2
    assert out[0].video_id == "vid1"
    assert out[0].title == "Track One"
    assert out[0].artists == "Artist A"
    assert out[0].duration == 178  # 2:58


def test_parse_album_tracks_trackheader_variant():
    out = parse_tracks(_load("album_tracks.json"))
    assert len(out) == 2
    assert out[0].video_id == "vida1"
    assert out[0].title == "Album Track"
    assert out[0].duration == 276  # 4:36


def test_parse_radio():
    out = parse_radio(_load("radio.json"))
    assert out[0].video_id == "vidr1"
    assert out[0].title == "Radio Track"
    assert out[0].duration == 322  # 5:22


def test_format_drift_raises():
    with pytest.raises(TvFormatError):
        parse_tracks({"contents": {"somethingElseRenderer": {}}})
