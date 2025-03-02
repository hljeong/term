from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing_extensions import Iterator, override
from term import Vec, W, cursor_to, f, w

from ref import Ref


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

    @override
    def render(self, hints: RenderHints) -> Iterator[Span]:
        yield self


class Term:
    def __init__(self):
        self.renderables: list[Renderable] = []

    def add(self, renderable: Renderable):
        self.renderables.append(renderable)

    def render(self):
        w("\x1b[2J")
        hints = RenderHints()
        for idx, renderable in enumerate(self.renderables):
            for span in renderable.render(hints):
                for dx, ch in enumerate(span.text):
                    w(cursor_to(Vec(0, idx) + span.pos + Vec(dx, 0)))
                    w(ch)
        f()


class Label(Renderable):
    def __init__(self, text: str | Ref[str]):
        self.text: Ref[str] = Ref.of(text)

    @override
    def render(self, hints: RenderHints) -> Iterator[Span]:
        yield Span(Vec(0, 0), self.text.value)
