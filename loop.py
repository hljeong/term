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

    def after_n_frames(self, func: Func, *, n: int):
        run_at: int = self.state.frame_count + n

        def wrapped():
            if self.state.frame_count == run_at:
                func()
                self.unregister(wrapped)

        self.register(wrapped)

    def after_n_seconds(self, func: Func, *, n: float):
        run_at: float = monotonic() + n

        def wrapped():
            if monotonic() >= run_at:
                func()
                self.unregister(wrapped)

        self.register(wrapped)

    def every_n_frames(self, func: Func, *, n: int, after: int = 0):
        if n <= 0:
            raise ValueError(f"n must > 0, got: {n}")

        run_at: int = self.state.frame_count + after

        def wrapped():
            nonlocal run_at
            if self.state.frame_count == run_at:
                func()
                run_at += n

        self.register(wrapped)

    def every_n_seconds(self, func: Func, *, n: float, after: float = 0):
        if n <= 0:
            raise ValueError(f"n must > 0, got: {n}")

        run_at: float = monotonic() + after

        def wrapped():
            nonlocal run_at
            current_time: float = monotonic()
            if current_time >= run_at:
                func()
                while run_at <= current_time:
                    run_at += n

        self.register(wrapped)

    def n_times_per_second(self, func: Func, *, n: int):
        self.every_n_seconds(func, n=1 / n)

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
