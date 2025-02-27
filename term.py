from __future__ import annotations

from contextlib import contextmanager
from dataclasses import dataclass, field
import itertools
from functools import cached_property
import os
from random import choice, choices
import string
import sys
from time import sleep
from typing import Iterator
from operator import attrgetter

from lambdas import Lx

D = os.get_terminal_size()
H, W = D.lines, D.columns

buffer = [[" " for _ in range(W)] for __ in range(H)]


@dataclass(frozen=True)
class Vec:
    x: int
    y: int

    def __repr__(self) -> str:
        return f"Vec({self.x}, {self.y})"

    def __str__(self) -> str:
        return f"({self.x}, {self.y})"

    def __iter__(self) -> Iterator[int]:
        return iter((self.x, self.y))

    def __neg__(self) -> Vec:
        return Vec(-self.x, -self.y)

    def __add__(self, v: Vec) -> Vec:
        return Vec(self.x + v.x, self.y + v.y)

    def __sub__(self, v: Vec) -> Vec:
        return self + (-v)

    def __mul__(self, c: int) -> Vec:
        return Vec(self.x * c, self.y * c)

    def __rmul__(self, c: int) -> Vec:
        return self * c

    def __floordiv__(self, c: int) -> Vec:
        return Vec(self.x // c, self.y // c)

    def __mod__(self, c: int) -> Vec:
        return Vec(self.x % c, self.y % c)


class InvalidColorError(Exception):
    pass


@dataclass(frozen=True)
class Color:
    r: int
    g: int
    b: int

    def __postinit__(self):
        good = 0 <= Lx < 256
        if not all(map(good, {self.r, self.g, self.b})):
            raise InvalidColorError(str(self))

    def __str__(self) -> str:
        return f"Color(r={self.r}, g={self.g}, b={self.b})"

    @property
    def ansi_fg(self) -> str:
        return f"\x1b[38;2;{self.r};{self.g};{self.b}m"

    @property
    def ansi_bg(self) -> str:
        return f"\x1b[48;2;{self.r};{self.g};{self.b}m"

    @staticmethod
    def hex(color) -> Color:
        r = int(color[1:3], 16)
        g = int(color[3:5], 16)
        b = int(color[5:7], 16)
        return Color(r, g, b)

    @staticmethod
    def hsl(color):
        raise NotImplementedError

    @staticmethod
    def coerce(color: Color | str) -> Color:
        if isinstance(color, Color):
            return color

        if isinstance(color, str):
            if color.startswith("#"):
                return Color.hex(color)

        raise InvalidColorError(repr(color))


RED = Color(255, 0, 0)
YELLOW = Color(255, 255, 0)


def cursor_to(v: Vec) -> str:
    return f"\x1b[{v.y + 1};{v.x + 1}H"


class ChangeBuffer:
    def __init__(self):
        self._data = {}

    def __setitem__(self, v: Vec, value: str):
        self._data[v] = value

    def __iter__(self) -> Iterator[tuple[Vec, str]]:
        yield from sorted(self._data.items(), key=lambda item: (item[0].y, item[0].x))

    def render(self) -> str:
        comps = []
        pv = Vec(-1, -1)
        for v, ch in self:
            if v.y == pv.y and v.x == pv.x + 1:
                comps.append(ch)
            else:
                comps.append(f"{cursor_to(v)}{ch}")
            pv = v

        s = "".join(comps)
        return s if s.endswith(RESET) else f"{s}{RESET}"

    def clear(self):
        self._data = {}


class Buffer:
    def __init__(self):
        self.buf = ChangeBuffer()

    # todo: nomenclature
    def add(self, x: int, y: int, span: Span):
        for dx, ch in enumerate(span.text):
            self.buf[Vec(x + dx, y)] = span.style.decorate(ch)

    def draw(self):
        w(self.buf.render())
        f()
        self.buf.clear()


@dataclass(frozen=True)
class Rect:
    pos: Vec
    dim: Vec

    @cached_property
    def lim(self) -> Vec:
        return self.pos + self.dim

    @staticmethod
    def from_lim(pos: Vec, lim: Vec) -> Rect:
        return Rect(pos, lim - pos)

    def __str__(self) -> str:
        return f"Rect(pos={self.pos}, dim={self.dim})"

    def __bool__(self) -> bool:
        return self.dim.x > 0 and self.dim.y > 0

    def __add__(self, off: Vec) -> Rect:
        return Rect(self.pos + off, self.dim)

    def __sub__(self, off: Vec) -> Rect:
        return self + (-off)

    def __matmul__(self, pos: Vec) -> Rect:
        return Rect(pos, self.dim)

    def __contains__(self, v: Vec) -> bool:
        return self.pos.x <= v.x < self.lim.x and self.pos.y <= v.y < self.lim.y

    def __and__(self, rect: Rect) -> Rect:
        return Rect.from_lim(
            Vec(max(self.pos.x, rect.pos.x), max(self.pos.y, rect.pos.y)),
            Vec(min(self.lim.x, rect.lim.x), min(self.lim.y, rect.lim.y)),
        )


class Renderable:
    # todo: nomenclature
    @property
    def spans(self) -> Iterator[Span]:
        raise NotImplementedError


@dataclass(frozen=True)
class Span(Renderable):
    @dataclass
    class Style:
        fg: Color | None = None
        bg: Color | None = None

        _decorator: str = field(init=False)

        def __post_init__(self):
            comps: list[str] = []

            if self.fg:
                comps.append(self.fg.ansi_fg)

            if self.bg:
                comps.append(self.bg.ansi_bg)

            self._decorator = "".join(comps)

        def __repr__(self) -> str:
            comps: list[str] = []

            if self.fg:
                comps.append(f"fg={self.fg}")

            if self.bg:
                comps.append(f"bg={self.bg}")

            return f"Span.Style({', '.join(comps)})"

        def decorate(self, s: str) -> str:
            return f"{self._decorator}{s}"

    pos: Vec
    text: str
    style: Style = Style()

    def __str__(self) -> str:
        comps: list[str] = [f"{self.text}", str(self.style)]
        return f"Span({', '.join(comps)}) @ {self.pos}"

    def __add__(self, off: Vec) -> Span:
        return Span(self.pos + off, self.text, self.style)

    def __sub__(self, off: Vec) -> Span:
        return self + (-off)

    def __matmul__(self, pos: Vec) -> Span:
        return Span(pos, self.text, self.style)

    @property
    def spans(self) -> Iterator[Span]:
        yield self

    @cached_property
    def rect(self) -> Rect:
        return Rect(self.pos, Vec(len(self.text), 1))


class View:
    def __init__(self, rect: Rect):
        self.rect = rect

    def __str__(self) -> str:
        return f"View(pos={self.rect.pos}, dim={self.rect.dim})"

    def clamp(self, rect: Rect, *, underflow_ok=False):
        if not underflow_ok and (
            self.rect.dim.x > rect.dim.x or self.rect.dim.y > rect.dim.y
        ):
            raise ValueError(f"{self} does not fit in {rect}")

        x, y = self.rect.pos
        x = min(x, rect.lim.x - self.rect.lim.x)
        x = max(x, rect.pos.x)
        y = min(y, rect.lim.y - self.rect.lim.y)
        y = max(y, rect.pos.y)

        self.rect @= Vec(x, y)

    def clip(self, span: Span) -> Span | None:
        if not (span.rect & self.rect):
            return None

        if self.rect.pos.x > span.pos.x:
            return Span(
                Vec(self.rect.pos.x, span.pos.y),
                span.text[self.rect.pos.x - span.pos.x :],
                style=span.style,
            )

        else:
            return Span(
                span.pos, span.text[: self.rect.lim.x - span.pos.x], style=span.style
            )


DEFAULT_VIEW = View(
    Rect(Vec(0, 0), Vec(*attrgetter("columns", "lines")(os.get_terminal_size())))
)


class Box(Renderable):
    def __init__(self, rect: Rect):
        self.rect: Rect = rect
        self.view: View = View(rect @ Vec(0, 0))
        self.children: list[Renderable] = []

    def add(self, renderable: Renderable):
        self.children.append(renderable)

    @property
    def spans(self) -> Iterator[Span]:
        for renderable in self.children:
            for span in renderable.spans:
                clipped = self.view.clip(span)
                if clipped is not None:
                    yield clipped + self.rect.pos


class Label(Renderable):
    def __init__(self, rect: Rect, text: str):
        self.rect: Rect = rect
        self.text: str = text

    @property
    def spans(self) -> Iterator[Span]:
        yield Span(self.rect.pos, self.text[: self.rect.dim.x])


class Block(Renderable):
    def __init__(self, rect: Rect, *, border=True, title: str = ""):
        self.rect: Rect = rect
        self.box: Box = Box(
            Rect.from_lim(
                rect.pos + Vec(1, 1),
                rect.lim - Vec(1, 1),
            )
        )
        self.border: bool = border
        self.title: Label = Label(
            Rect(rect.pos + Vec(1, 0), rect.dim - Vec(2, 0)), title
        )

    def add(self, renderable: Renderable):
        self.box.add(renderable)

    @property
    def spans(self) -> Iterator[Span]:
        if self.border:
            if self.rect.dim.y == 1:
                if self.rect.dim.x == 1:
                    yield Span(self.rect.pos, "·")

                elif self.rect.dim.x > 1:
                    yield Span(self.rect.pos, "─" * self.rect.dim.x)

            elif self.rect.dim.y > 1:
                if self.rect.dim.x == 1:
                    for dy in range(self.rect.dim.y):
                        yield Span(self.rect.pos + Vec(0, dy), "│")

                else:
                    yield Span(
                        self.rect.pos, "".join(["┌", "─" * (self.rect.dim.x - 2), "┐"])
                    )
                    for dy in range(1, self.rect.dim.y - 1):
                        yield Span(self.rect.pos + Vec(0, dy), "│")
                        yield Span(self.rect.pos + Vec(self.rect.dim.x - 1, dy), "│")
                    yield Span(
                        self.rect.pos + Vec(0, self.rect.dim.y - 1),
                        "".join(["└", "─" * (self.rect.dim.x - 2), "┘"]),
                    )

        yield from self.title.spans
        yield from self.box.spans


class Screen:
    def __init__(self, box: Box = Box(DEFAULT_VIEW.rect), view: View = DEFAULT_VIEW):
        self.box = box
        self.view = view

    def draw(self):
        buf = ChangeBuffer()
        for span in self.box.spans:
            for dx, ch in enumerate(span.text):
                buf[span.pos + Vec(dx, 0)] = span.style.decorate(ch)

        w(buf.render())
        f()


w = sys.stdout.write
f = sys.stdout.flush


@contextmanager
def new_buffer():
    buffer = ChangeBuffer()
    yield buffer
    w(buffer.render())
    f()


RESET = "\x1b[0m"
HIDE_CURSOR = "\x1b[?25l"
SHOW_CURSOR = "\x1b[?25h"


def setup():
    w(HIDE_CURSOR)
    for _ in range(H - 1):
        w("\n")
    w(cursor_to(Vec(0, 0)))
    f()


def teardown():
    w(cursor_to(DEFAULT_VIEW.rect.lim - Vec(0, 2)))
    w("\n")
    w(SHOW_CURSOR)
    f()


@contextmanager
def go():
    setup()
    try:
        yield
    finally:
        teardown()


with go():
    # buf = Buffer()
    # s = choices(string.ascii_lowercase, k=H * W)
    # for i in range(5000):
    #     # buf.add(i * 6, 0, Span("lorem ipsum dolor sit amet", Span.Style(fg=YELLOW)))
    #     for x in range(W):
    #         for y in range(H):
    #             buf.add(x, y, Span(s[(x + y + i) % (H * W)]))
    #     buf.draw()
    # with new_buffer() as b:
    #     for x in range(W):
    #         for y in range(H):
    #             b[x, y] = "o" if (x + y) % 2 == i % 2 else "x"
    # sleep(1)

    s = Screen()
    b = Block(Rect(Vec(0, 0), Vec(20, 10)), title="hi")
    b.add(Label(Rect(Vec(0, 0), Vec(20, 1)), "first item"))
    b.add(Label(Rect(Vec(-3, 1), Vec(20, 1)), "second item"))
    b.add(Label(Rect(Vec(0, 2), Vec(20, 1)), "third item"))
    s.box.add(b)
    s.draw()
