from __future__ import annotations

from dataclasses import dataclass
from time import monotonic, sleep
from typing import Callable


Func = Callable[[], None]


@dataclass
class State:
    f: int = 0
    t_start_abs: float = 0
    t_last_abs: float = 0
    t_abs: float = 0

    @property
    def t_last(self) -> float:
        return self.t_last_abs - self.t_start_abs

    @property
    def t(self) -> float:
        return self.t_abs - self.t_start_abs


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
        self.state.t_abs = monotonic()
        for func in self.funcs:
            func()
        self.state.f += 1
        self.state.t_last_abs = self.state.t_abs

    def start(self):
        self.state.t_start_abs = monotonic()
        next_frame_time: float = self.state.t_start_abs
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
