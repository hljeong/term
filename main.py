from enum import Enum
from random import random

from layout import Padding
from loop import L
from ref import Ref, RefFunc
from term import go, lorem
from term2 import Block, Color, Dim, Direction, Layout, Term, Text


def main():
    N = 10
    T = 99
    L.after(L.stop, seconds=N)

    class Status(Enum):
        Queueing = 0
        Running = 1
        Success = 2
        Failed = 3

        def __format__(self, spec):
            if spec == "c":
                match self:
                    case Status.Queueing:
                        return "[yellow]queueing[/yellow]"

                    case Status.Running:
                        return "[cyan]running[/cyan]"

                    case Status.Success:
                        return "[green]success[/green]"

                    case Status.Failed:
                        return "[red]failed[/red]"

            return str(self)

    tasks = [Status.Queueing] * T

    def start_task(idx):
        assert tasks[idx] == Status.Queueing
        tasks[idx] = Status.Running

    def finish_task(idx):
        assert tasks[idx] == Status.Running
        if random() < 0.5:
            tasks[idx] = Status.Success
        else:
            tasks[idx] = Status.Failed

    def biased_random():
        r = random()
        return r * r

    for idx in range(T):
        start = biased_random() * N
        end = (1 - biased_random()) * N
        if end < start:
            start, end = end, start
        L.after((lambda idx_: lambda: start_task(idx_))(idx), seconds=start)
        L.after((lambda idx_: lambda: finish_task(idx_))(idx), seconds=end)

    t: Term = Term(
        layout=Layout(
            # direction=Direction.VERTICAL,
            direction=Direction.Horizontal,
            padding=Padding(1, 2),
        ),
        border=True,
    )
    L.n_times_per_second(t.render, n=10)

    seconds: Ref[float] = Ref(getter=lambda: L.state.t)
    text: Ref[str] = RefFunc(lambda seconds: format(seconds, ".2f"))(seconds)
    text2: Ref[str] = Ref(lorem[:20])
    L.interval(lambda: text2.set_value(text2.value[:-1]), seconds=1, after=1)

    # t(Text(text))
    # with t(Block(border=False)):
    #     t(Text(text2))

    with t(Block(layout=Layout(direction=Direction.Vertical, gap=1))):
        for idx in range(T):
            t(Text(f"{idx + 1}: "))

    with t(Block(layout=Layout(direction=Direction.Vertical, gap=1))):
        for idx in range(T):
            t(Text(Ref(getter=(lambda idx_: lambda: format(tasks[idx_], "c"))(idx))))

    with go():
        L.start()


if __name__ == "__main__":
    main()
