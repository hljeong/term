from loop import L
from ref import Ref
from term import go, lorem
from term2 import Label, Term


def main():
    N = 5
    L.after(L.stop, seconds=N)

    t: Term = Term()

    second: Ref[int] = Ref(0)
    L.interval(lambda: second.set_value(second.value + 1), seconds=1, after=1)

    label: Ref[str] = second.apply(str)
    t.add(Label(label))

    label2: Ref[str] = Ref(lorem[:20])
    L.interval(lambda: label2.set_value(label2.value[:-1]), seconds=1, after=1)
    t.add(Label(label2))

    L.n_times_per_second(t.render, n=30)

    with go():
        L.start()


if __name__ == "__main__":
    main()
