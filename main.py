from random import random

from loop import L
from ref import Ref, RefFunc
from term import go, lorem
from term2 import Block, Border, Color, Direction, Term, Text, Thing


def main():
    N = 5
    L.after(L.stop, seconds=N)

    t: Term = Term()

    # b: Border = Border(t.block)
    # # todo: this sucks
    # t.block += b
    # top: Block
    # bottom: Block
    # top, bottom = b.block.split(direction=Direction.VERTICAL)
    #
    # seconds: Ref[float] = Ref(getter=lambda: L.state.t)
    # text: Ref[str] = RefFunc(lambda seconds: format(seconds, ".2f"))(seconds)
    # top.add(Text(text))
    #
    # text2: Ref[str] = Ref(lorem[:20])
    # L.interval(lambda: text2.set_value(text2.value[:-1]), seconds=1, after=1)
    # bottom.add(Text(text2))

    left: Block
    right: Block
    left, right = t.block.split()

    thing1: Thing = Thing(left.box)
    left.add(thing1)

    thing2: Thing = Thing(right.box)
    right.add(thing2)

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
