from random import random

from layout import Padding
from loop import L
from ref import Ref, RefFunc
from term import go, lorem
from term2 import Block, Color, Dim, Direction, Term, Text


def main():
    N = 5
    L.after(L.stop, seconds=N)

    t: Term = Term()

    t.block.layout.direction = Direction.VERTICAL
    t.block.layout.padding = Padding(1, 2)
    t.block.layout.gap = 1
    t.block.border = True

    seconds: Ref[float] = Ref(getter=lambda: L.state.t)
    text: Ref[str] = RefFunc(lambda seconds: format(seconds, ".2f"))(seconds)
    t.block.add(Text(text))

    text2: Ref[str] = Ref(lorem[:20])
    L.interval(lambda: text2.set_value(text2.value[:-1]), seconds=1, after=1)
    t.block.add(Block(Text(text2), border=True))

    # hue1: float = random()
    # hue2: float = random()
    #
    # def change_color():
    #     nonlocal hue1, hue2
    #
    #     thing1.color = Color.hsl(hue1, 1, 0.7)
    #     thing2.color = Color.hsl(hue2, 1, 0.7)
    #
    #     hue1 += 0.005
    #     if hue1 > 1:
    #         hue1 -= 1
    #
    #     hue2 += 0.01
    #     if hue2 > 1:
    #         hue2 -= 1
    #
    # L.interval(change_color, seconds=0.1)

    L.n_times_per_second(t.render, n=10)

    with go():
        L.start()


if __name__ == "__main__":
    main()
