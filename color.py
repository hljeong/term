from __future__ import annotations

from dataclasses import dataclass
from math import floor
from typing import Callable, ClassVar


class InvalidColorError(Exception):
    pass


@dataclass(frozen=True)
class Color:
    r: int
    g: int
    b: int

    @dataclass(frozen=True)
    class SystemColor:
        name: str
        ansi_fg: str
        ansi_bg: str

    NO_COLOR: ClassVar[int] = 1
    SYSTEM_COLOR: ClassVar[int] = 2
    SYSTEM_COLORS: ClassVar[list[SystemColor]] = [
        SystemColor("black", "\x1b[30m", "\x1b[40m"),
        SystemColor("red", "\x1b[31m", "\x1b[41m"),
        SystemColor("green", "\x1b[32m", "\x1b[42m"),
        SystemColor("yellow", "\x1b[33m", "\x1b[43m"),
        SystemColor("blue", "\x1b[34m", "\x1b[44m"),
        SystemColor("magenta", "\x1b[35m", "\x1b[45m"),
        SystemColor("cyan", "\x1b[36m", "\x1b[46m"),
        SystemColor("light gray", "\x1b[37m", "\x1b[47m"),
        SystemColor("dark gray", "\x1b[90m", "\x1b[100m"),
        SystemColor("light red", "\x1b[91m", "\x1b[101m"),
        SystemColor("light green", "\x1b[92m", "\x1b[102m"),
        SystemColor("light yellow", "\x1b[93m", "\x1b[103m"),
        SystemColor("light blue", "\x1b[94m", "\x1b[104m"),
        SystemColor("light magenta", "\x1b[95m", "\x1b[105m"),
        SystemColor("light cyan", "\x1b[96m", "\x1b[106m"),
        SystemColor("white", "\x1b[97m", "\x1b[107m"),
    ]

    def __postinit__(self):
        match self.r, self.g, self.b:
            case Color.SYSTEM_COLOR, c, _:
                if not 0 <= c < 16:
                    raise InvalidColorError(str(self))

            case r, g, b:
                good = lambda v: 0 <= v < 256
                if not all(map(good, {r, g, b})):
                    raise InvalidColorError(str(self))

    def __str__(self) -> str:
        match self.r, self.g, self.b:
            case Color.SYSTEM_COLOR, c, _:
                return Color.SYSTEM_COLORS[c].name

            case r, g, b:
                return f"Color({r=}, {g=}, {b=})"

    @property
    def ansi_fg(self) -> str:
        match self.r, self.g, self.b:
            case Color.NO_COLOR, _, _:
                return ""

            case Color.SYSTEM_COLOR, c, _:
                return Color.SYSTEM_COLORS[c].ansi_fg

            case r, g, b:
                return f"\x1b[38;2;{r};{g};{b}m"

    @property
    def ansi_bg(self) -> str:
        match self.r, self.g, self.b:
            case Color.NO_COLOR, _, _:
                return ""

            case Color.SYSTEM_COLOR, c, _:
                return Color.SYSTEM_COLORS[c].ansi_bg

            case r, g, b:
                return f"\x1b[48;2;{r};{g};{b}m"

    @staticmethod
    def system(color: int) -> Color:
        return Color(Color.SYSTEM_COLOR, color, 0)

    @staticmethod
    def hex(color: str) -> Color:
        if not color.startswith("#") or len(color) != 7:
            raise ValueError(f"invalid hex color: {color!r}")

        try:
            r = int(color[1:3], 16)
            g = int(color[3:5], 16)
            b = int(color[5:7], 16)
        except ValueError:
            raise ValueError(f"invalid hex color: {color!r}")
        return Color(r, g, b)

    # see: https://gist.github.com/ciembor/1494530
    @staticmethod
    def hsl(h: float, s: float, l: float):
        scale: Callable[[float], int] = lambda v: floor(v * 255)

        if s == 0:
            return Color(scale(l), scale(l), scale(l))

        else:

            def hue2rgb(p: float, q: float, t: float) -> int:
                v: float

                if t < 0:
                    t += 1
                if t > 1:
                    t -= 1
                if t < 1 / 6:
                    v = p + (q - p) * 6 * t
                elif t < 1 / 2:
                    v = q
                elif t < 2 / 3:
                    v = p + (q - p) * (2 / 3 - t) * 6
                else:
                    v = p

                return scale(v)

            q: float = l * (1 + s) if l < 0.5 else l + s - l * s
            p: float = 2 * l - q
            return Color(
                hue2rgb(p, q, h + 1 / 3),
                hue2rgb(p, q, h),
                hue2rgb(p, q, h - 1 / 3),
            )

    @staticmethod
    def coerce(color: Color | str) -> Color:
        if isinstance(color, Color):
            return color

        if isinstance(color, str):
            if color.startswith("#"):
                return Color.hex(color)

        raise InvalidColorError(repr(color))

    NONE: ClassVar[Color] = ...  # type: ignore
    BLACK: ClassVar[Color] = ...  # type: ignore
    RED: ClassVar[Color] = ...  # type: ignore
    GREEN: ClassVar[Color] = ...  # type: ignore
    YELLOW: ClassVar[Color] = ...  # type: ignore
    BLUE: ClassVar[Color] = ...  # type: ignore
    MAGENTA: ClassVar[Color] = ...  # type: ignore
    CYAN: ClassVar[Color] = ...  # type: ignore
    LIGHT_GRAY: ClassVar[Color] = ...  # type: ignore
    DARK_GRAY: ClassVar[Color] = ...  # type: ignore
    LIGHT_RED: ClassVar[Color] = ...  # type: ignore
    LIGHT_GREEN: ClassVar[Color] = ...  # type: ignore
    LIGHT_YELLOW: ClassVar[Color] = ...  # type: ignore
    LIGHT_BLUE: ClassVar[Color] = ...  # type: ignore
    LIGHT_MAGENTA: ClassVar[Color] = ...  # type: ignore
    LIGHT_CYAN: ClassVar[Color] = ...  # type: ignore
    WHITE: ClassVar[Color] = ...  # type: ignore


Color.NONE = Color(Color.NO_COLOR, -1, -1)
Color.BLACK = Color.system(0)
Color.RED = Color.system(1)
Color.GREEN = Color.system(2)
Color.YELLOW = Color.system(3)
Color.BLUE = Color.system(4)
Color.MAGENTA = Color.system(5)
Color.CYAN = Color.system(6)
Color.LIGHT_GRAY = Color.system(7)
Color.DARK_GRAY = Color.system(8)
Color.LIGHT_RED = Color.system(9)
Color.LIGHT_GREEN = Color.system(10)
Color.LIGHT_YELLOW = Color.system(11)
Color.LIGHT_BLUE = Color.system(12)
Color.LIGHT_MAGENTA = Color.system(13)
Color.LIGHT_CYAN = Color.system(14)
Color.WHITE = Color.system(15)
