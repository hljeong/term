from abc import ABC, abstractmethod
from typing_extensions import override
from term import Vec, W, cursor_to, f, w

from ref import Ref


class Renderable(ABC):
    @abstractmethod
    def render(self):
        raise NotImplementedError


class Term:
    def __init__(self):
        self.renderables: list[Renderable] = []

    def add(self, renderable: Renderable):
        self.renderables.append(renderable)

    def render(self):
        w("\x1b[2J")
        for idx, renderable in enumerate(self.renderables):
            w(cursor_to(Vec(0, idx)))
            renderable.render()
        f()


class Label(Renderable):
    def __init__(self, text: str | Ref[str]):
        self.text: Ref[str] = Ref.of(text)

    @override
    def render(self):
        w(self.text.value[:W])
