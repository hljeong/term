import os
import sys

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

RESET = "\x1b[0m"
HIDE_CURSOR = "\x1b[?25l"
SHOW_CURSOR = "\x1b[?25h"

w(HIDE_CURSOR)

# empty = ChangeBuffer()
# for x in range(W):
#     for y in range(H):
#         empty[x, y] = " "
# w(render(empty))
for y in range(H - 1):
    w("\n")

delta = ChangeBuffer()
for x in range(W):
    for y in range(H):
        delta[x, y] = "o" if (x + y) % 2 == 0 else "x"
        # delta[x, y] = str(y)[0]

w(render(delta))
w(render(delta))

from time import sleep

sleep(1)

w(SHOW_CURSOR)

w("\n")
