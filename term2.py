from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from color import Color
from layout import Box, Dim, Direction, Fixed, Layout, LayoutInfo, Sizing
from random import random
from typing import Iterator
from typing_extensions import override

from ref import Ref
from term import H, Vec, W, cursor_to, f, w


class Renderable(ABC):
    NEXT_ID: int = 1

    def __init__(self):
        self.id: int = Renderable.NEXT_ID
        Renderable.NEXT_ID += 1

    @abstractmethod
    def size(self, render_table: RenderTable):
        raise NotImplementedError

    @abstractmethod
    def place(self, render_table: RenderTable):
        raise NotImplementedError

    @abstractmethod
    def render(self, render_table: RenderTable) -> Iterator[Span]:
        raise NotImplementedError


@dataclass
class RenderInfo:
    pos: Vec = Vec(0, 0)  # todo: fix
    dim: Dim = Dim(0, 0)  # todo: fix


class RenderTable:
    def __init__(self):
        self.table: dict[int, RenderInfo] = {}

    def __contains__(self, thing: Renderable) -> bool:
        return thing.id in self.table

    def __getitem__(self, thing: Renderable) -> RenderInfo:
        if thing not in self:
            self.table[thing.id] = RenderInfo()
        return self.table[thing.id]

    def __setitem__(self, thing: Renderable, render_info: RenderInfo):
        self.table[thing.id] = render_info


@dataclass
class Span:
    pos: Vec
    text: str
    color: Color = Color.NONE

    def __add__(self, off: Vec) -> Span:
        return Span(self.pos + off, self.text, self.color)


class Block(Renderable):
    def __init__(
        self, *contents: Renderable, layout: Layout | None = None, border=False
    ):
        super().__init__()
        self.layout: Layout = layout or Layout()
        self.border: bool = border
        self.contents: list[Renderable] = list(contents)

    def add(self, thing: Renderable):
        self.contents.append(thing)

    def __iadd__(self, thing: Renderable) -> Block:
        self.add(thing)
        return self

    def __iter__(self) -> Iterator[Renderable]:
        yield from self.contents

    def __len__(self) -> int:
        return len(self.contents)

    @override
    def size(self, render_table: RenderTable):
        for thing in self:
            thing.size(render_table)
        render_table[self].dim = self.layout.size(self.contents, render_table)

        if self.border:
            render_table[self].dim.w += 2
            render_table[self].dim.h += 2

    @override
    def place(self, render_table: RenderTable):
        for thing in self:
            thing.place(render_table)
        self.layout.place(self.contents, render_table)

        if self.border:
            for thing in self:
                render_table[thing].pos += Vec(1, 1)

    @override
    def render(self, render_table: RenderTable) -> Iterator[Span]:
        if self.border:
            match render_table[self].dim:
                case Dim(0, _) | Dim(_, 0):
                    pass

                case Dim(1, 1):
                    yield Span(Vec(0, 0), "·")

                case Dim(w, 1):
                    yield Span(Vec(0, 0), "─" * w)

                case Dim(1, h):
                    for dy in range(h):
                        yield Span(Vec(0, dy), "│")

                case Dim(w, h):
                    yield Span(Vec(0, 0), "".join(["┌", "─" * (w - 2), "┐"]))
                    for dy in range(1, h - 1):
                        yield Span(Vec(0, dy), "│")
                        yield Span(Vec(w - 1, dy), "│")
                    yield Span(Vec(0, h - 1), "".join(["└", "─" * (w - 2), "┘"]))

        for thing in self.contents:
            for span in thing.render(render_table):
                # todo: clip
                yield span + render_table[thing].pos


class Term:
    def __init__(self):
        self.layout: Layout = Layout(sizing=Sizing(Fixed(W), Fixed(H)))
        self.block: Block = Block()

    def add(self, thing: Renderable):
        self.block += thing

    def render(self):
        w("\x1b[2J")
        render_table = RenderTable()
        self.block.size(render_table)
        self.block.place(render_table)
        for span in self.block.render(render_table):
            for dx, ch in enumerate(span.text):
                w(cursor_to(span.pos + Vec(dx, 0)))
                w(f"{span.color.ansi_bg}{ch}\x1b[0m")
        f()


class Text(Renderable):
    def __init__(self, text: str | Ref[str]):
        super().__init__()
        self.text: Ref[str] = Ref.of(text)

    @override
    def size(self, render_table: RenderTable):
        render_table[self].dim = Dim(len(self.text.value), 1)

    @override
    def place(self, render_table: RenderTable):
        pass

    @override
    def render(self, render_table: RenderTable) -> Iterator[Span]:
        yield Span(Vec(0, 0), self.text.value)
