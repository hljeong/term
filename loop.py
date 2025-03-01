from __future__ import annotations

from dataclasses import dataclass
from math import ceil
from time import monotonic, sleep
from types import FrameType
from typing import Callable


Func = Callable[[], None]


@dataclass
class State:
    frame_count: int = 0


class Loop:
    def __init__(self, *, max_fps: float | None = 120):
        self.max_fps: float | None = max_fps

        self.funcs: list[Func] = []
        self.state: State = State()
        self.stopped: bool = False

    def register(self, func: Func):
        self.funcs.append(func)

    def unregister(self, func: Func):
        self.funcs = [f for f in self.funcs if f is not func]

    def after(self, func: Func, *, seconds: float):
        if seconds <= 0:
            raise ValueError(f"seconds must > 0, got: {seconds}")

        when: float = monotonic() + seconds

        def wrapped():
            if monotonic() >= when:
                func()
                self.unregister(wrapped)

        self.register(wrapped)

    def interval(self, func: Func, *, seconds: float, after: float = 0):
        if seconds <= 0:
            raise ValueError(f"seconds must > 0, got: {seconds}")

        when: float = monotonic() + after

        def wrapped():
            nonlocal when
            now: float = monotonic()
            if now >= when:
                func()
                while when <= now:
                    when += seconds

        self.register(wrapped)

    def n_times_per_second(self, func: Func, *, n: int):
        self.interval(func, seconds=1 / n)

    def dispatch(self):
        for func in self.funcs:
            func()
        self.state.frame_count += 1

    def start(self):
        next_frame_time: float = monotonic()
        while not self.stopped:
            if self.max_fps is None:
                self.dispatch()
            else:
                current_time: float = monotonic()
                if current_time < next_frame_time:
                    sleep(next_frame_time - current_time)
                self.dispatch()
                next_frame_time += 1 / self.max_fps

    def stop(self):
        self.stopped = True


L = Loop()
