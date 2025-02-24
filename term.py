from contextlib import contextmanager, redirect_stdout
from dataclasses import dataclass, field
import os
import sys
from time import sleep

from lambdas import Lx

D = os.get_terminal_size()
H, W = D.lines, D.columns

buffer = [[" " for _ in range(W)] for __ in range(H)]


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

    def __str__(self):
        return f"Color(r={self.r}, g={self.g}, b={self.b})"

    @property
    def ansi_fg(self):
        return f"\x1b[38;2;{self.r};{self.g};{self.b}m"

    @property
    def ansi_bg(self):
        return f"\x1b[48;2;{self.r};{self.g};{self.b}m"

    @staticmethod
    def hex(color):
        r = int(color[1:3], 16)
        g = int(color[3:5], 16)
        b = int(color[5:7], 16)
        return Color(r, g, b)

    @staticmethod
    def hsl(color):
        raise NotImplementedError

    @staticmethod
    def coerce(color):
        if isinstance(color, Color):
            return color

        if isinstance(color, str):
            if color.startswith("#"):
                return Color.hex(color)

        raise InvalidColorError(repr(color))


RED = Color(255, 0, 0)
YELLOW = Color(255, 255, 0)


class ChangeBuffer:
    def __init__(self):
        self._data = {}

    def __setitem__(self, idx, value):
        self._data[idx] = value

    def __iter__(self):
        return iter(
            sorted(self._data.items(), key=lambda item: (item[0][1], item[0][0]))
        )

    def render(self) -> str:
        comps = []
        px, py = None, None
        for (x, y), ch in self:
            if px is not None and (x == px + 1 and y == py):
                comps.append(ch)
            else:
                comps.append(f"\x1b[{y + 1};{x + 1}H{ch}")

            px, py = x, y

        s = "".join(comps)
        return s if s.endswith(RESET) else f"{s}{RESET}"

    def clear(self):
        self._data = {}


@dataclass
class Span:
    @dataclass
    class Style:
        fg: Color | None = None
        bg: Color | None = None

        _decorator: str = field(init=False)

        def __post_init__(self):
            if self.fg is not None:
                self.fg = Color.coerce(self.fg)

            if self.bg is not None:
                self.bg = Color.coerce(self.bg)

            comps: list[str] = []

            if self.fg:
                comps.append(self.fg.ansi_fg)

            if self.bg:
                comps.append(self.bg.ansi_bg)

            self._decorator = "".join(comps)

        def __repr__(self):
            comps: list[str] = []

            if self.fg:
                comps.append(f"fg={self.fg}")

            if self.bg:
                comps.append(f"bg={self.bg}")

            return f"Span.Style({', '.join(comps)})"

        def decorate(self, s: str) -> str:
            return f"{self._decorator}{s}"

    text: str
    style: Style = Style()

    _rendered: str = field(init=False)

    def __str__(self) -> str:
        comps: list[str] = [f"{self.text}", str(self.style)]
        return f"Span({', '.join(comps)})"


class Buffer:
    def __init__(self):
        self.buf = ChangeBuffer()

    # todo: nomenclature
    def add(self, x: int, y: int, span: Span):
        for dx, ch in enumerate(span.text):
            self.buf[x + dx, y] = span.style.decorate(ch)

    def draw(self):
        w(self.buf.render())
        f()
        self.buf.clear()


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
    f()


def teardown():
    w(SHOW_CURSOR)
    w("\n")
    f()


@contextmanager
def go():
    setup()
    try:
        yield
    finally:
        teardown()


with go():
    buf = Buffer()
    for i in range(5):
        buf.add(0, i, Span("lorem ipsum dolor sit amet", Span.Style(fg=YELLOW)))
        buf.draw()
        # with new_buffer() as b:
        #     for x in range(W):
        #         for y in range(H):
        #             b[x, y] = "o" if (x + y) % 2 == i % 2 else "x"
        sleep(1)
