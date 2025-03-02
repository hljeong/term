from loop import L
from ref import Ref, RefFunc
from term import go, lorem
from term2 import Label, Term


def main():
    N = 5
    L.after(L.stop, seconds=N)

    t: Term = Term()

    seconds: Ref[float] = Ref(getter=lambda: L.state.t)
    label: Ref[str] = RefFunc(lambda seconds: format(seconds, ".2f"))(seconds)
    t.add(Label(label))

    label2: Ref[str] = Ref(lorem[:20])
    L.interval(lambda: label2.set_value(label2.value[:-1]), seconds=1, after=1)
    t.add(Label(label2))

    L.n_times_per_second(t.render, n=30)

    with go():
        L.start()


if __name__ == "__main__":
    main()
