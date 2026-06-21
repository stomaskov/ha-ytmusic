"""Pure parsers for TVHTML5 youtubei responses -> Track / SearchItem.

No I/O. Browse/library/radio use tileRenderer; search uses lockupViewModel.
Validated against real captures (docs/superpowers/tv-format-findings.md).
"""

from __future__ import annotations

from ..backend import SearchItem
from ..models import Track
from .errors import TvFormatError


def _nav(node, *path):
    cur = node
    for key in path:
        if cur is None:
            return None
        try:
            cur = cur[key]
        except (KeyError, IndexError, TypeError):
            return None
    return cur


def parse_duration(text: str | None) -> int | None:
    if not text or ":" not in text:
        return None
    parts = text.split(":")
    if not all(p.isdigit() for p in parts):
        return None
    secs = 0
    for p in parts:
        secs = secs * 60 + int(p)
    return secs


def find_keys(node, key: str) -> list:
    out: list = []
    if isinstance(node, dict):
        for k, v in node.items():
            if k == key and isinstance(v, dict):
                out.append(v)
            else:
                out.extend(find_keys(v, key))
    elif isinstance(node, list):
        for x in node:
            out.extend(find_keys(x, key))
    return out


def find_tiles(node) -> list[dict]:
    return find_keys(node, "tileRenderer")


# ---- tileRenderer field extraction (browse/library/album/artist/radio variants) ----
def _tile_video_id(t: dict) -> str | None:
    return _nav(t, "onSelectCommand", "watchEndpoint", "videoId") or _nav(
        t,
        "metadata",
        "tileMetadataRenderer",
        "title",
        "runs",
        0,
        "navigationEndpoint",
        "watchEndpoint",
        "videoId",
    )


def _tile_browse_id(t: dict) -> str | None:
    return (
        _nav(
            t,
            "metadata",
            "tileMetadataRenderer",
            "title",
            "runs",
            0,
            "navigationEndpoint",
            "browseEndpoint",
            "browseId",
        )
        or _nav(t, "onSelectCommand", "browseEndpoint", "browseId")
        or _nav(t, "onSelectCommand", "watchEndpoint", "playlistId")
    )


def _tile_title(t: dict) -> str:
    return (
        _nav(t, "metadata", "tileMetadataRenderer", "title", "runs", 0, "text")
        or _nav(t, "metadata", "tileMetadataRenderer", "title", "simpleText")
        or _nav(t, "header", "trackTileHeaderRenderer", "title", "simpleText")
        or ""
    )


def _tile_subtitle(t: dict) -> str:
    for line in _nav(t, "metadata", "tileMetadataRenderer", "lines") or []:
        for it in _nav(line, "lineRenderer", "items") or []:
            txt = _nav(it, "lineItemRenderer", "text", "simpleText") or _nav(
                it, "lineItemRenderer", "text", "runs", 0, "text"
            )
            if txt:
                return txt
    return ""


def _tile_thumbnail(t: dict) -> str | None:
    thumbs = (
        _nav(t, "header", "tileHeaderRenderer", "thumbnail", "thumbnails")
        or _nav(t, "header", "trackTileHeaderRenderer", "thumbnail", "thumbnails")
        or []
    )
    return thumbs[-1]["url"] if thumbs else None


def _tile_duration(t: dict) -> int | None:
    for ov in _nav(t, "header", "tileHeaderRenderer", "thumbnailOverlays") or []:
        txt = _nav(ov, "thumbnailOverlayTimeStatusRenderer", "text", "simpleText")
        if txt:
            return parse_duration(txt)
    return parse_duration(
        _nav(t, "header", "trackTileHeaderRenderer", "duration", "simpleText")
    )


def _kind_for(browse_id: str | None, content_type: str | None) -> str:
    if browse_id:
        if browse_id.startswith("MPRE"):
            return "album"
        if browse_id.startswith("UC"):
            return "artist"
        return "playlist"
    if content_type and "VIDEO" in content_type:
        return "video"
    return "song"


def extract_tile(t: dict) -> SearchItem | None:
    vid = _tile_video_id(t)
    bid = None if vid else _tile_browse_id(t)
    if not vid and not bid:
        return None
    return SearchItem(
        kind=_kind_for(bid, t.get("contentType")),
        id=vid or bid,
        title=_tile_title(t),
        subtitle=_tile_subtitle(t),
        thumbnail=_tile_thumbnail(t),
    )


def tile_to_track(item: SearchItem, t: dict) -> Track:
    return Track(
        video_id=item.id,
        title=item.title,
        artists=item.subtitle,
        album=None,
        thumbnail=item.thumbnail,
        duration=_tile_duration(t),
    )


# ---- lockupViewModel (search) ----
_LOCKUP_KIND = {
    "LOCKUP_CONTENT_TYPE_MUSIC": "song",
    "LOCKUP_CONTENT_TYPE_VIDEO": "video",
    "LOCKUP_CONTENT_TYPE_CHANNEL": "artist",
    "LOCKUP_CONTENT_TYPE_ALBUM": "album",
    "LOCKUP_CONTENT_TYPE_PLAYLIST": "playlist",
}


def _lockup_to_item(lv: dict) -> SearchItem | None:
    cid = lv.get("contentId")
    if not cid:
        return None
    sources = _nav(lv, "contentImage", "thumbnailViewModel", "image", "sources") or []
    return SearchItem(
        kind=_LOCKUP_KIND.get(lv.get("contentType", ""), "song"),
        id=cid,
        title=_nav(lv, "metadata", "lockupMetadataViewModel", "title", "content") or "",
        subtitle=_nav(
            lv,
            "metadata",
            "lockupMetadataViewModel",
            "metadata",
            "contentMetadataViewModel",
            "metadataRows",
            0,
            "metadataParts",
            0,
            "text",
            "content",
        )
        or "",
        thumbnail=sources[-1]["url"] if sources else None,
    )


def _require(resp: dict, envelope_key: str) -> None:
    if not find_keys(resp, envelope_key):
        raise TvFormatError(
            f"expected {envelope_key} in TV response (format may have changed)"
        )


# ---- endpoint parsers ----
def parse_search(resp: dict, filter: str | None = None) -> list[SearchItem]:
    _require(resp, "sectionListRenderer")
    items = []
    for lv in find_keys(resp, "lockupViewModel"):
        item = _lockup_to_item(lv)
        if item:
            items.append(item)
    return items


def parse_library_playlists(resp: dict) -> list[dict]:
    _require(resp, "tvBrowseRenderer")
    out = []
    for t in find_tiles(resp):
        if _tile_video_id(t):  # keep only playlist tiles (no videoId)
            continue
        item = extract_tile(t)
        if item:
            out.append(
                {"id": item.id, "title": item.title, "thumbnail": item.thumbnail}
            )
    return out


def parse_tracks(resp: dict) -> list[Track]:
    _require(resp, "tvBrowseRenderer")
    out = []
    for t in find_tiles(resp):
        if _tile_video_id(t):
            item = extract_tile(t)
            if item:
                out.append(tile_to_track(item, t))
    return out


def parse_radio(resp: dict) -> list[Track]:
    _require(resp, "singleColumnWatchNextResults")
    out = []
    for t in find_tiles(resp):
        if _tile_video_id(t):
            item = extract_tile(t)
            if item:
                out.append(tile_to_track(item, t))
    return out
