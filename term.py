from contextlib import contextmanager
import os
import sys
from time import sleep

D = os.get_terminal_size()
H, W = D.lines, D.columns

buffer = [[" " for _ in range(W)] for __ in range(H)]


class ChangeBuffer:
    def __init__(self):
        self._data = {}

    def __setitem__(self, idx, value):
        self._data[idx] = value

    def __iter__(self):
        return iter(
            sorted(self._data.items(), key=lambda item: (item[0][1], item[0][0]))
        )


def render(buf):
    s = ""
    px, py = None, None
    for (x, y), ch in buf:
        if px is not None and (x == px + 1 and y == py):
            s += ch
        else:
            s += f"\x1b[{y + 1};{x + 1}H{ch}"

        px, py = x, y

    if not s.endswith(RESET):
        s += RESET

    return s


w = sys.stdout.write
f = sys.stdout.flush


@contextmanager
def new_buffer():
    buffer = ChangeBuffer()
    yield buffer
    w(render(buffer))
    f()


RESET = "\x1b[0m"
HIDE_CURSOR = "\x1b[?25l"
SHOW_CURSOR = "\x1b[?25h"


def setup():
    w(HIDE_CURSOR)
    for y in range(H - 1):
        w("\n")
    f()


def teardown():
    w(SHOW_CURSOR)
    w("\n")


@contextmanager
def go():
    setup()
    try:
        yield
    finally:
        teardown()


with go():
    for i in range(5):
        with new_buffer() as b:
            for x in range(W):
                for y in range(H):
                    b[x, y] = "o" if (x + y) % 2 == i % 2 else "x"
        sleep(1)
