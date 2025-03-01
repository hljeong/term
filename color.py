from __future__ import annotations

from dataclasses import dataclass
from typing import ClassVar


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

    SYSTEM_COLOR: ClassVar[int] = 1
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
            case Color.SYSTEM_COLOR, c, _:
                return Color.SYSTEM_COLORS[c].ansi_fg

            case r, g, b:
                return f"\x1b[38;2;{r};{g};{b}m"

    @property
    def ansi_bg(self) -> str:
        match self.r, self.g, self.b:
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

    @staticmethod
    def hsl(h: float, s: float, l: float):
        raise NotImplementedError

    @staticmethod
    def coerce(color: Color | str) -> Color:
        if isinstance(color, Color):
            return color

        if isinstance(color, str):
            if color.startswith("#"):
                return Color.hex(color)

        raise InvalidColorError(repr(color))


BLACK: Color = Color.system(0)
RED: Color = Color.system(1)
GREEN: Color = Color.system(2)
YELLOW: Color = Color.system(3)
BLUE: Color = Color.system(4)
MAGENTA: Color = Color.system(5)
CYAN: Color = Color.system(6)
LIGHT_GRAY: Color = Color.system(7)
DARK_GRAY: Color = Color.system(8)
LIGHT_RED: Color = Color.system(9)
LIGHT_GREEN: Color = Color.system(10)
LIGHT_YELLOW: Color = Color.system(11)
LIGHT_BLUE: Color = Color.system(12)
LIGHT_MAGENTA: Color = Color.system(13)
LIGHT_CYAN: Color = Color.system(14)
WHITE: Color = Color.system(15)
