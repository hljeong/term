from __future__ import annotations

from loop import L
from typing import Callable, Generic, TypeVar

T = TypeVar("T")
U = TypeVar("U")


class Ref(Generic[T]):
    def __init__(self, value: T):
        self.value: T = value

    def set_value(self, value: T):
        self.value = value

    def apply(self, func: Callable[[T], U], *, interval=0.2) -> Ref[U]:
        ref: Ref[U] = Ref(func(self.value))
        L.interval(lambda: ref.set_value(func(self.value)), seconds=interval)
        return ref

    @staticmethod
    def of(value: T | Ref[T]) -> Ref[T]:
        if isinstance(value, Ref):
            return value

        else:
            return Ref(value)
