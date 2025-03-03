from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import ClassVar, Iterator, TypeAlias

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

    def __iter__(self):
        yield self.w
        yield self.h


class Fixed:
    def __init__(self, value: int):
        self.value: int = value


class Fit:
    pass


@dataclass
class Sizing:
    w: Fixed | Fit = Fit()
    h: Fixed | Fit = Fit()


@dataclass
class Padding:
    top: int = 0
    right: int = -1
    bottom: int = -1
    left: int = -1

    def __post_init__(self):
        if self.right < 0:
            self.right = self.top

        if self.bottom < 0:
            self.bottom = self.top

        if self.left < 0:
            self.left = self.right


@dataclass
class LayoutInfo:
    pos: Vec
    dim: Vec


@dataclass
class Layout:
    sizing: Sizing = Sizing(Fit(), Fit())
    direction: Direction = Direction.HORIZONTAL
    padding: Padding = field(default_factory=Padding)
    gap: int = 0

    # def apply(self, contents: Iterable[Renderable]) -> Iterator[tuple[Renderable, Vec]]:
    def apply(self, contents):
        pos: Vec = Vec(self.padding.left, self.padding.top)
        match self.direction:
            case Direction.HORIZONTAL:
                for thing in contents:
                    yield thing, LayoutInfo(pos=pos)
                    # todo: .dim is not guaranteed to exist
                    pos += Vec(thing.dim.w + self.gap, 0)

            case Direction.VERTICAL:
                for thing in contents:
                    yield thing, LayoutInfo(pos=pos)
                    # todo: .dim is not guaranteed to exist
                    pos += Vec(0, thing.dim.h + self.gap)

    # todo: type annotation
    def size(self, contents, render_table) -> Dim:
        dim: Dim = Dim(0, 0)
        match self.direction:
            case Direction.HORIZONTAL:
                for thing in contents:
                    w, h = render_table[thing].dim
                    dim.w += w
                    dim.h = max(dim.h, h)

                dim.w += max(0, len(contents) - 1) * self.gap

            case Direction.VERTICAL:
                for thing in contents:
                    w, h = render_table[thing].dim
                    dim.h += render_table[thing].dim.h
                    dim.w = max(dim.w, w)

                dim.h += max(0, len(contents) - 1) * self.gap

        dim.w += self.padding.left + self.padding.right
        dim.h += self.padding.top + self.padding.bottom
        return dim

    # todo: type annotation
    # todo: enforce .size() first then .place()
    def place(self, contents, render_table):
        pos: Vec = Vec(self.padding.left, self.padding.top)
        match self.direction:
            case Direction.HORIZONTAL:
                for thing in contents:
                    render_table[thing].pos = pos
                    pos += Vec(render_table[thing].dim.w + self.gap, 0)

            case Direction.VERTICAL:
                for thing in contents:
                    render_table[thing].pos = pos
                    pos += Vec(0, render_table[thing].dim.h + self.gap)


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
