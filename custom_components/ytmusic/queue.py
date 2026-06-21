"""Pure, I/O-free play queue state machine."""

from __future__ import annotations

import random
from collections.abc import Callable

from .models import RepeatMode, Track


class PlayQueue:
    def __init__(self) -> None:
        self._items: list[Track] = []
        self.index: int = 0
        self.shuffle: bool = False
        self.repeat: RepeatMode = RepeatMode.OFF

    def current(self) -> Track | None:
        if not self._items or not (0 <= self.index < len(self._items)):
            return None
        return self._items[self.index]

    def tracks_remaining(self) -> int:
        return max(0, len(self._items) - self.index - 1)

    def set_queue(self, tracks: list[Track], start: int = 0) -> None:
        self._items = list(tracks)
        self.index = start if 0 <= start < len(self._items) else 0

    def enqueue(self, tracks: list[Track]) -> None:
        self._items.extend(tracks)

    def enqueue_next(self, tracks: list[Track]) -> None:
        at = self.index + 1
        self._items[at:at] = tracks

    def remove(self, index: int) -> None:
        if not 0 <= index < len(self._items):
            return
        del self._items[index]
        if index < self.index:
            self.index -= 1
        elif index == self.index and self.index >= len(self._items):
            self.index = max(0, len(self._items) - 1)

    def move(self, src: int, dst: int) -> None:
        if not (0 <= src < len(self._items) and 0 <= dst < len(self._items)):
            return
        cur = self.index
        self._items.insert(dst, self._items.pop(src))
        if src == cur:
            self.index = dst
        elif src < cur <= dst:
            self.index -= 1
        elif dst <= cur < src:
            self.index += 1

    def clear(self) -> None:
        self._items = []
        self.index = 0

    def jump(self, index: int) -> Track | None:
        if not 0 <= index < len(self._items):
            return None
        self.index = index
        return self.current()

    def next(self) -> Track | None:
        if not self._items:
            return None
        if self.repeat is RepeatMode.ONE:
            return self.current()
        if self.index + 1 < len(self._items):
            self.index += 1
            return self.current()
        if self.repeat is RepeatMode.ALL:
            self.index = 0
            return self.current()
        return None

    def previous(self) -> Track | None:
        if not self._items:
            return None
        if self.index > 0:
            self.index -= 1
        return self.current()

    def set_shuffle(
        self, on: bool, shuffler: Callable[[list], None] = random.shuffle
    ) -> None:
        self.shuffle = on
        if on and self._items:
            playing = self._items[self.index]
            rest = self._items[: self.index] + self._items[self.index + 1 :]
            shuffler(rest)
            self._items = [playing, *rest]
            self.index = 0

    def set_repeat(self, mode: RepeatMode) -> None:
        self.repeat = mode

    def as_list(self) -> list[dict]:
        return [t.as_dict() for t in self._items]
