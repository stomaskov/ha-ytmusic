#!/usr/bin/env python3
"""Capture raw YouTube Music TV (youtubei, TVHTML5 context) responses for every
endpoint the ytmusic OAuth backend needs, so the parser can be built against real
structure. Creds via env; output saved to ./captures/ (gitignored — contains your
library data).

    YTM_CLIENT_ID='...' YTM_CLIENT_SECRET='...' .venv/bin/python scripts/tv_capture.py
"""
from __future__ import annotations

import json
import os
import time
from pathlib import Path

import requests
from ytmusicapi.auth.oauth import OAuthCredentials

BASE = "https://music.youtube.com/youtubei/v1/"
TV = {"clientName": "TVHTML5", "clientVersion": "7.20240701.00.00", "hl": "en", "gl": "US"}
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:88.0) Gecko/20100101 Firefox/88.0"
OUT = Path("captures")


def main() -> None:
    cid = os.environ.get("YTM_CLIENT_ID") or input("client_id: ").strip()
    csec = os.environ.get("YTM_CLIENT_SECRET") or input("client_secret: ").strip()
    creds = OAuthCredentials(client_id=cid, client_secret=csec)
    code = creds.get_code()
    print(f"\nOpen {code['verification_url']} enter {code['user_code']}")
    input("Authorize, then Enter…")
    tok = creds.token_from_code(code["device_code"])["access_token"]
    OUT.mkdir(exist_ok=True)

    def post(name: str, endpoint: str, body: dict) -> dict:
        b = dict(body)
        b["context"] = {"client": dict(TV), "user": {}}
        r = requests.post(
            BASE + endpoint + "?prettyPrint=false",
            json=b,
            headers={
                "Authorization": f"Bearer {tok}",
                "Content-Type": "application/json",
                "X-Goog-Request-Time": str(int(time.time())),
                "User-Agent": UA,
            },
        )
        j = r.json()
        (OUT / f"{name}.json").write_text(json.dumps(j, indent=1))
        top = list(j.get("contents", j).keys()) if isinstance(j, dict) else "?"
        print(f"  {name:28s} HTTP {r.status_code}  top={top}")
        return j

    # library (known to work) + the unknowns we need to map:
    lib = post("library_playlists", "browse", {"browseId": "FEmusic_liked_playlists"})
    songs = post("search_songs", "search", {"query": "daft punk", "params": _search_params("songs")})
    for f in ("albums", "artists", "playlists"):
        post(f"search_{f}", "search", {"query": "daft punk", "params": _search_params(f)})

    # auto-extract ids from the fresh responses and capture the remaining endpoints.
    albums = json.loads((OUT / "search_albums.json").read_text())
    playlist_id = _first_id(lib, prefix="VLPL")               # a real user playlist (tile)
    video_id = _lockup_id(songs, "LOCKUP_CONTENT_TYPE_MUSIC") or _first_id(songs, video=True)
    artist_id = _lockup_id(songs, "LOCKUP_CONTENT_TYPE_CHANNEL")  # a UC channel
    album_id = (_lockup_id(albums, "LOCKUP_CONTENT_TYPE_ALBUM")
                or _lockup_id(albums, "LOCKUP_CONTENT_TYPE_PLAYLIST")
                or _first_id(albums, prefix="VLOLAK") or _first_id(albums, prefix="VL"))
    print(f"\nauto ids -> playlist={playlist_id} album={album_id} artist={artist_id} video={video_id}")
    if playlist_id:
        post("playlist", "browse", {"browseId": playlist_id})
    if album_id:
        post("album", "browse", {"browseId": album_id})
    if artist_id:
        post("artist", "browse", {"browseId": artist_id})
    if video_id:
        post("radio", "next", {"videoId": video_id, "playlistId": f"RDAMVM{video_id}"})
    print("\nDone. captures/: library, search_*, playlist, album, artist, radio.")


def _find_tiles(node) -> list[dict]:
    out: list[dict] = []
    if isinstance(node, dict):
        for k, v in node.items():
            if k == "tileRenderer" and isinstance(v, dict):
                out.append(v)
            else:
                out.extend(_find_tiles(v))
    elif isinstance(node, list):
        for x in node:
            out.extend(_find_tiles(x))
    return out


def _nav(node, *path):
    cur = node
    for k in path:
        if cur is None:
            return None
        try:
            cur = cur[k]
        except (KeyError, IndexError, TypeError):
            return None
    return cur


def _tile_browse_id(t: dict) -> str | None:
    return (
        _nav(t, "metadata", "tileMetadataRenderer", "title", "runs", 0,
             "navigationEndpoint", "browseEndpoint", "browseId")
        or _nav(t, "onSelectCommand", "browseEndpoint", "browseId")
        or _nav(t, "onSelectCommand", "watchEndpoint", "playlistId")
    )


def _first_id(resp: dict, prefix: str | None = None, video: bool = False) -> str | None:
    for t in _find_tiles(resp):
        if video:
            vid = _nav(t, "onSelectCommand", "watchEndpoint", "videoId")
            if vid:
                return vid
            continue
        bid = _tile_browse_id(t)
        if bid and (prefix is None or bid.startswith(prefix)):
            return bid
    return None


def _find_lockups(node) -> list[dict]:
    out: list[dict] = []
    if isinstance(node, dict):
        for k, v in node.items():
            if k == "lockupViewModel" and isinstance(v, dict):
                out.append(v)
            else:
                out.extend(_find_lockups(v))
    elif isinstance(node, list):
        for x in node:
            out.extend(_find_lockups(x))
    return out


def _lockup_id(resp: dict, content_type: str) -> str | None:
    for lv in _find_lockups(resp):
        if lv.get("contentType") == content_type and lv.get("contentId"):
            return lv["contentId"]
    return None


def _search_params(filter: str) -> str:
    # ytmusicapi computes these; print them so we can pin them in endpoints.py
    from ytmusicapi.parsers.search import get_search_params
    return get_search_params(filter, None, False) or ""


if __name__ == "__main__":
    main()
