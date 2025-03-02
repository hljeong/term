from __future__ import annotations

from typing import Callable, Generic, TypeVar

from loop import L

T = TypeVar("T")
U = TypeVar("U")


class Ref(Generic[T]):
    def __init__(
        self, value: T | None = None, *, getter: Callable[[], T] | None = None
    ):
        if not ((value is None) ^ (getter is None)):
            raise ValueError("provide either value or getter")

        self._value: T | None = value
        self._get: Callable[[], T] | None = getter

    @property
    def value(self) -> T:
        if self._get is None:
            assert self._value is not None
            return self._value

        else:
            assert self._get is not None
            return self._get()

    def set_value(self, value: T):
        if self._get is None:
            self._value = value

        else:
            raise Exception("cannot set value of getter ref")

    @staticmethod
    def dereference(value: T | Ref[T]) -> T:
        if isinstance(value, Ref):
            return value.value

        else:
            return value

    @staticmethod
    def of(value: T | Ref[T]) -> Ref[T]:
        if isinstance(value, Ref):
            return value

        else:
            return Ref(value)


class RefFunc(Generic[T]):
    def __init__(self, func: Callable[..., T]):
        self.func: Callable[..., T] = func

    def __call__(self, *args, **kwargs):
        ref: Ref[T] = Ref(
            getter=lambda: self.func(
                *map(Ref.dereference, args),
                **{k: Ref.dereference(v) for k, v in kwargs.items()},
            )
        )
        return ref
