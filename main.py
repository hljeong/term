from loop import L
from ref import Ref
from term import go, lorem
from term2 import Label, Term


def main():
    N = 5
    L.after_n_seconds(L.stop, n=N)

    t: Term = Term()

    second: Ref[int] = Ref(0)
    L.every_n_seconds(lambda: second.set_value(second.value + 1), n=1, after=1)

    label: Ref[str] = second.apply(str)
    t.add(Label(label))

    label2: Ref[str] = Ref(lorem[:20])
    L.every_n_seconds(lambda: label2.set_value(label2.value[:-1]), n=1, after=1)
    t.add(Label(label2))

    L.n_times_per_second(t.render, n=30)

    with go():
        L.start()


if __name__ == "__main__":
    main()
