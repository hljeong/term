from contextlib import contextmanager
from dataclasses import dataclass
from random import random
from rich.console import Console
from rich.columns import Columns
from threading import Lock, Thread
from time import monotonic, sleep
from typing import Callable, Generic, TypeVar, cast

from lambdas import L

T = TypeVar("T")


def loop_in_bg(func, interval=0.5):
    def f():
        while True:
            func()
            sleep(interval)

    t = Thread(target=f)
    t.daemon = True

    return t


class Watcher:
    @dataclass
    class Watched(Generic[T]):
        getter: Callable[[], T]
        last: T
        callback: Callable[[T], None]

    def __init__(self):
        self.watched = []
        self.thread = None

    def watch(self, getter, callback):
        value = getter()
        callback(value)
        self.watched.append(Watcher.Watched(getter, value, callback))

    def dispatch(self):
        for watched in self.watched:
            new = watched.getter()
            if new != watched.last:
                watched.callback(new)
            watched.last = new

    def start(self, interval=0.5):
        if self.thread is None:
            self.thread = loop_in_bg(self.dispatch, interval=interval)
            self.thread.start()


class Buffered:
    def __init__(self, getter, interval=0.5):
        self._getter = getter
        self.interval = interval
        self.value = getter()

        def buffer():
            self.value = self._getter()

        self.thread = loop_in_bg(buffer, interval=interval)
        self.thread.start()

    def getter(self):
        return self.value


class Ref:
    def __init__(self, value):
        self.value = value
        self.getter = lambda: self.value


@contextmanager
def timer():
    t_start = monotonic()
    yield lambda: monotonic() - t_start


raw_data = {c: 0.0 for c in "abcdefghijklmnopqrstuvwxyz"}


def f():
    with timer() as t:
        while t() < 30:
            for c in raw_data:
                raw_data[c] += random() - 0.45
            sleep(0.1)


cons = Console()

tracked = ["a", "e", "i", "o", "u"]
data = {c: (lambda c_: Buffered(lambda: raw_data[c_]))(c) for c in tracked}


def colored(s, color="black"):
    return f"[{color}]{s}[/{color}]"


class ForTheLackOfANameAltogether:
    def __init__(self, description, condition):
        self.description = description
        self.condition = condition

    def __rich__(self):
        description = (
            self.description() if callable(self.description) else self.description
        )
        return colored(description, "green" if self.condition() else "red")


things = []
for c in tracked:
    things.append(
        ForTheLackOfANameAltogether(
            (lambda c_: lambda: f"{c_} = {data[c_].getter():.2f} > 10")(c),
            L(data[c].getter) > 10,
        )
    )


def render():
    cons.clear()
    for thing in things:
        cons.print(thing)
    # for c in tracked[: cons.height - 1]:
    #     x = data[c].getter()
    #     cons.print(f"[{'red' if x < 10 else 'green'}]{c} {x:.3f}")


# w = Watcher()
# for c in tracked:
#     w.watch((lambda c: lambda: d[c])(c), lambda _: None)
# w.start(0.1)

# loop_in_bg(render, 0.1).start()

# f()
