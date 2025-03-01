from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Iterator

from term import Vec


class Direction(Enum):
    HORIZONTAL = "horizontal"
    VERTICAL = "vertical"


@dataclass
class Dim:
    w: int
    h: int

    def __post_init__(self):
        self.w = max(0, self.w)
        self.h = max(0, self.h)


@dataclass
class Box:
    pos: Vec
    dim: Dim

    def split(
        self,
        *,
        n: int = 2,
        direction: Direction = Direction.HORIZONTAL,
    ) -> Iterator[Box]:
        if n < 2:
            raise ValueError(f"n must >= 2, got: {n}")

        match direction:
            case Direction.HORIZONTAL:
                w: int
                n_wide: int
                w, n_wide = divmod(self.dim.w, n)
                next_pos: Vec = self.pos
                for idx in range(n):
                    box: Box = Box(next_pos, Dim(w + int(idx < n_wide), self.dim.h))
                    yield box
                    next_pos += Vec(box.dim.w, 0)

            case Direction.VERTICAL:
                h: int
                n_tall: int
                h, n_tall = divmod(self.dim.h, n)
                next_pos: Vec = self.pos
                for idx in range(n):
                    box: Box = Box(next_pos, Dim(self.dim.w, h + int(idx < n_tall)))
                    yield box
                    next_pos += Vec(0, box.dim.h)
