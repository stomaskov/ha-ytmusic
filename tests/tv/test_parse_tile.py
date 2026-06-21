import json
from pathlib import Path

from custom_components.ytmusic.tv.parse import (
    extract_tile,
    find_tiles,
    parse_duration,
    tile_to_track,
)

FIX = Path(__file__).parent.parent / "fixtures" / "tv"


def _load(name):
    return json.loads((FIX / name).read_text())


def test_parse_duration():
    assert parse_duration("4:01") == 241
    assert parse_duration("1:02:03") == 3723
    assert parse_duration(None) is None
    assert parse_duration("nonsense") is None


def test_extract_song_tile():
    item = extract_tile(_load("tile_song.json")["tileRenderer"])
    assert item.kind in ("song", "video")
    assert item.id == "vid_song"
    assert item.title == "Song One"
    assert item.subtitle == "Artist A"
    assert item.thumbnail


def test_extract_playlist_tile_uses_browse_id():
    item = extract_tile(_load("tile_playlist.json")["tileRenderer"])
    assert item.kind in ("playlist", "album", "artist")
    assert item.id.startswith(("VL", "MPRE", "UC"))


def test_extract_tile_without_ids_returns_none():
    assert extract_tile({"metadata": {}}) is None


def test_find_tiles_walks_nested():
    node = {
        "a": {"items": [{"tileRenderer": {"x": 1}}, {"other": {}}]},
        "b": {"tileRenderer": {"y": 2}},
    }
    assert len(find_tiles(node)) == 2


def test_tile_to_track_sets_duration():
    tile = _load("tile_song.json")["tileRenderer"]
    item = extract_tile(tile)
    track = tile_to_track(item, tile)
    assert track.video_id == "vid_song"
    assert track.duration is not None
