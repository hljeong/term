from random import random

from layout import Padding
from loop import L
from ref import Ref, RefFunc
from term import go, lorem
from term2 import Block, Color, Dim, Direction, Layout, Term, Text


def main():
    N = 5
    L.after(L.stop, seconds=N)

    t: Term = Term(
        layout=Layout(
            direction=Direction.VERTICAL,
            padding=Padding(1, 2),
            gap=1,
        ),
        border=True,
    )
    L.n_times_per_second(t.render, n=10)

    seconds: Ref[float] = Ref(getter=lambda: L.state.t)
    text: Ref[str] = RefFunc(lambda seconds: format(seconds, ".2f"))(seconds)
    text2: Ref[str] = Ref(lorem[:20])
    L.interval(lambda: text2.set_value(text2.value[:-1]), seconds=1, after=1)

    t(Text(text))
    with t(Block(border=True)):
        t(Text(text2))

    with go():
        L.start()


if __name__ == "__main__":
    main()
