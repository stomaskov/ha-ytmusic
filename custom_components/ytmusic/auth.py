"""Auth helpers: browser-cookie header building and YTMusic client construction."""

from __future__ import annotations

import hashlib
import time

from ytmusicapi import YTMusic
from ytmusicapi.auth.oauth import OAuthCredentials

from .const import (
    AUTH_OAUTH,
    CONF_AUTH_METHOD,
    CONF_CLIENT_ID,
    CONF_CLIENT_SECRET,
    CONF_COOKIE,
    CONF_OAUTH_TOKEN,
)

_DEFAULT_UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0 Safari/537.36"
)
_ORIGIN = "https://music.youtube.com"


def parse_cookie(cookie: str) -> dict[str, str]:
    out: dict[str, str] = {}
    for part in cookie.split(";"):
        part = part.strip()
        if "=" in part:
            k, v = part.split("=", 1)
            out[k.strip()] = v.strip()
    return out


def make_sapisidhash(
    papisid: str, origin: str = _ORIGIN, now: int | None = None
) -> str:
    ts = int(time.time()) if now is None else now
    digest = hashlib.sha1(f"{ts} {papisid} {origin}".encode()).hexdigest()
    return f"SAPISIDHASH {ts}_{digest}"


def build_browser_headers(cookie: str, user_agent: str | None = None) -> dict:
    parsed = parse_cookie(cookie)
    papisid = parsed.get("__Secure-3PAPISID") or parsed.get("SAPISID")
    if not papisid:
        raise ValueError(
            "Cookie is missing __Secure-3PAPISID / SAPISID — not a valid YT Music session"
        )
    return {
        "Cookie": cookie,
        "Authorization": make_sapisidhash(papisid),
        "X-Goog-AuthUser": "0",
        "origin": _ORIGIN,
        "User-Agent": user_agent or _DEFAULT_UA,
        "Accept": "*/*",
        "Content-Type": "application/json",
    }


def build_client(entry_data: dict) -> YTMusic:
    """Construct an authenticated YTMusic client. Run in the executor."""
    if entry_data.get(CONF_AUTH_METHOD) == AUTH_OAUTH:
        creds = OAuthCredentials(
            client_id=entry_data[CONF_CLIENT_ID],
            client_secret=entry_data[CONF_CLIENT_SECRET],
        )
        return YTMusic(auth=entry_data[CONF_OAUTH_TOKEN], oauth_credentials=creds)
    return YTMusic(auth=build_browser_headers(entry_data[CONF_COOKIE]))
