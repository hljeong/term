from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from color import Color
from layout import Box, Dim, Direction
from random import random
from typing import Iterator
from typing_extensions import override

from ref import Ref
from term import H, Vec, W, cursor_to, f, w


@dataclass
class RenderHints:
    pass


class Renderable(ABC):
    @abstractmethod
    def render(self, hints: RenderHints) -> Iterator[Span]:
        raise NotImplementedError


@dataclass
class Span(Renderable):
    pos: Vec
    text: str
    color: Color = Color.NONE

    def __add__(self, off: Vec) -> Span:
        return Span(self.pos + off, self.text, self.color)

    @override
    def render(self, hints: RenderHints) -> Iterator[Span]:
        yield self


@dataclass
class Block(Renderable):
    box: Box
    contents: list[Renderable] = field(default_factory=list)

    def add(self, thing: Renderable):
        self.contents.append(thing)

    def __iadd__(self, thing: Renderable) -> Block:
        self.add(thing)
        return self

    def split(
        self,
        *,
        n: int = 2,
        direction: Direction = Direction.HORIZONTAL,
    ) -> Iterator[Block]:
        if self.contents:
            raise RuntimeError("cannot split nonempty block")

        for box in self.box.split(n=n, direction=direction):
            block: Block = Block(box)
            self += block
            yield block

    @override
    def render(self, hints: RenderHints) -> Iterator[Span]:
        for thing in self.contents:
            for span in thing.render(hints):
                # todo: clip
                yield span + self.box.pos


class Term:
    def __init__(self):
        self.block: Block = Block(Box(Vec(0, 0), Dim(W, H)))

    def add(self, thing: Renderable):
        self.block += thing

    def render(self):
        w("\x1b[2J")
        hints = RenderHints()
        for span in self.block.render(hints):
            for dx, ch in enumerate(span.text):
                w(cursor_to(span.pos + Vec(dx, 0)))
                w(f"{span.color.ansi_bg}{ch}\x1b[0m")
        f()


class Border(Renderable):
    def __init__(self, block: Block):
        self.box: Box = block.box
        # todo: already failing separating layout and content
        self.block: Block = Block(
            Box(Vec(0, 0), Dim(self.box.dim.w - 2, self.box.dim.h - 2))
        )

        self.spans: list[Span] = []
        match self.box.dim:
            case Dim(0, _) | Dim(_, 0):
                pass

            case Dim(1, 1):
                self.spans.append(Span(Vec(0, 0), "·"))

            case Dim(w, 1):
                self.spans.append(Span(Vec(0, 0), "─" * w))

            case Dim(1, h):
                for dy in range(h):
                    self.spans.append(Span(self.box.pos + Vec(0, dy), "│"))

            case Dim(w, h):
                self.spans.append(
                    Span(
                        self.box.pos,
                        "".join(["┌", "─" * (w - 2), "┐"]),
                    )
                )
                for dy in range(1, h - 1):
                    self.spans.append(Span(self.box.pos + Vec(0, dy), "│"))
                    self.spans.append(Span(self.box.pos + Vec(w - 1, dy), "│"))
                self.spans.append(
                    Span(
                        self.box.pos + Vec(0, h - 1),
                        "".join(["└", "─" * (w - 2), "┘"]),
                    )
                )

    @override
    def render(self, hints: RenderHints) -> Iterator[Span]:
        yield from self.spans
        for span in self.block.render(hints):
            yield span + Vec(1, 1)


class Text(Renderable):
    def __init__(self, text: str | Ref[str]):
        self.text: Ref[str] = Ref.of(text)

    @override
    def render(self, hints: RenderHints) -> Iterator[Span]:
        yield Span(Vec(0, 0), self.text.value)


class Thing(Renderable):
    def __init__(self, box: Box):
        self.box: Box = box
        self.color: Color = Color.hsl(random(), 1, 0.7)

    @override
    def render(self, hints: RenderHints) -> Iterator[Span]:
        for dy in range(self.box.dim.h):
            yield Span(Vec(0, dy), " " * self.box.dim.w, self.color)
