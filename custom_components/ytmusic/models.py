"""Data models for the YouTube Music integration."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class RepeatMode(StrEnum):
    OFF = "off"
    ONE = "one"
    ALL = "all"


@dataclass(frozen=True, slots=True)
class Track:
    video_id: str
    title: str
    artists: str
    album: str | None = None
    thumbnail: str | None = None
    duration: int | None = None

    def as_dict(self) -> dict:
        return {
            "video_id": self.video_id,
            "title": self.title,
            "artists": self.artists,
            "album": self.album,
            "thumbnail": self.thumbnail,
            "duration": self.duration,
        }


@dataclass(frozen=True, slots=True)
class LyricLine:
    text: str
    start_ms: int | None = None

    def as_dict(self) -> dict:
        return {"text": self.text, "start_ms": self.start_ms}


@dataclass(frozen=True, slots=True)
class LyricsResult:
    lines: list[LyricLine]
    synced: bool

    def as_dict(self) -> dict:
        return {"lines": [ln.as_dict() for ln in self.lines], "synced": self.synced}
