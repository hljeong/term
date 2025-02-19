from contextlib import contextmanager
from dataclasses import dataclass
from random import random
from rich.console import Console
from rich.columns import Columns
from threading import Lock, Thread
from time import monotonic, sleep
from typing import Callable, Generic, TypeVar

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


@contextmanager
def timer():
    t_start = monotonic()
    yield lambda: monotonic() - t_start


d = {c: 0.0 for c in "abcdefghijklmnopqrstuvwxyz"}


def f():
    with timer() as t:
        while t() < 10:
            for c in d:
                d[c] += random() - 0.4
            sleep(0.1)


cons = Console()


def render():
    cons.clear()
    for c in sorted(d, key=lambda c: -d[c])[: cons.height - 1]:
        cons.print(f"[{'red' if d[c] < 10 else 'green'}]{c} {d[c]:.3f}")


w = Watcher()
for c in d:
    w.watch((lambda c: lambda: d[c])(c), lambda _: None)
w.start(0.1)

loop_in_bg(render, 0.1).start()

f()
