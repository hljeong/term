from __future__ import annotations

from abc import ABC, abstractmethod
from contextlib import contextmanager
from dataclasses import dataclass, field
from color import Color
from layout import Box, Dim, Direction, Fixed, Layout, LayoutInfo, Sizing
from random import random
import re
from types import TracebackType
from typing import ContextManager, Iterator
from typing_extensions import override

from ref import Ref
from term import H, Vec, W, cursor_to, f, w


class Renderable(ABC):
    NEXT_ID: int = 1

    def __init__(self):
        self.id: int = Renderable.NEXT_ID
        Renderable.NEXT_ID += 1

    def add(self, thing: Renderable):
        pass

    @abstractmethod
    def size(self, render_table: RenderTable):
        raise NotImplementedError

    @abstractmethod
    def place(self, render_table: RenderTable):
        raise NotImplementedError

    @abstractmethod
    def render(self, render_table: RenderTable) -> Iterator[Span]:
        raise NotImplementedError


@dataclass
class RenderInfo:
    pos: Vec = field(default_factory=lambda: Vec(0, 0))
    dim: Dim = field(default_factory=lambda: Dim(0, 0))


class RenderTable:
    def __init__(self):
        self.table: dict[int, RenderInfo] = {}

    def __contains__(self, thing: Renderable) -> bool:
        return thing.id in self.table

    def __getitem__(self, thing: Renderable) -> RenderInfo:
        if thing not in self:
            self.table[thing.id] = RenderInfo()
        return self.table[thing.id]

    def __setitem__(self, thing: Renderable, render_info: RenderInfo):
        self.table[thing.id] = render_info


@dataclass
class Style:
    fg_color: Color = Color.NONE
    bg_color: Color = Color.NONE


@dataclass
class Span:
    pos: Vec
    text: str
    style: Style = field(default_factory=Style)

    def __add__(self, off: Vec) -> Span:
        return Span(self.pos + off, self.text, self.style)


class Block(Renderable):
    def __init__(
        self, *contents: Renderable, layout: Layout | None = None, border=False
    ):
        super().__init__()
        self.layout: Layout = layout or Layout()
        self.border: bool = border
        self.contents: list[Renderable] = list(contents)

    @override
    def add(self, thing: Renderable):
        self.contents.append(thing)

    def __iter__(self) -> Iterator[Renderable]:
        yield from self.contents

    def __len__(self) -> int:
        return len(self.contents)

    @override
    def size(self, render_table: RenderTable):
        for thing in self:
            thing.size(render_table)
        render_table[self].dim = self.layout.size(self.contents, render_table)

        if self.border:
            render_table[self].dim.w += 2
            render_table[self].dim.h += 2

    @override
    def place(self, render_table: RenderTable):
        for thing in self:
            thing.place(render_table)
        self.layout.place(self.contents, render_table)

        if self.border:
            for thing in self:
                render_table[thing].pos += Vec(1, 1)

    @override
    def render(self, render_table: RenderTable) -> Iterator[Span]:
        if self.border:
            match render_table[self].dim:
                case Dim(0, _) | Dim(_, 0):
                    pass

                case Dim(1, 1):
                    yield Span(Vec(0, 0), "·")

                case Dim(w, 1):
                    yield Span(Vec(0, 0), "─" * w)

                case Dim(1, h):
                    for dy in range(h):
                        yield Span(Vec(0, dy), "│")

                case Dim(w, h):
                    yield Span(Vec(0, 0), "".join(["┌", "─" * (w - 2), "┐"]))
                    for dy in range(1, h - 1):
                        yield Span(Vec(0, dy), "│")
                        yield Span(Vec(w - 1, dy), "│")
                    yield Span(Vec(0, h - 1), "".join(["└", "─" * (w - 2), "┘"]))

        for thing in self.contents:
            for span in thing.render(render_table):
                span += render_table[thing].pos

                # clip
                # todo: this is incredibly disgusting
                if self.border:
                    if span.pos.x >= render_table[self].dim.w - 1:
                        continue

                    if span.pos.y >= render_table[self].dim.h - 1:
                        continue

                    if span.pos.y < 1:
                        continue

                    if span.pos.x <= 1 - len(span.text):
                        continue

                    if span.pos.x < 1:
                        yield Span(
                            Vec(1, span.pos.y), span.text[1 - span.pos.x :], span.style
                        )

                    else:
                        yield Span(
                            span.pos,
                            span.text[: render_table[self].dim.w - 1 - span.pos.x],
                            span.style,
                        )

                else:
                    if span.pos.x >= render_table[self].dim.w:
                        continue

                    if span.pos.y >= render_table[self].dim.h:
                        continue

                    if span.pos.y < 0:
                        continue

                    if span.pos.x <= -len(span.text):
                        continue

                    if span.pos.x < 0:
                        yield Span(
                            Vec(0, span.pos.y), span.text[-span.pos.x :], span.style
                        )

                    else:
                        yield Span(
                            span.pos,
                            span.text[: render_table[self].dim.w - span.pos.x],
                            span.style,
                        )


class Term:
    def __init__(self, *, layout: Layout | None = None, border=False):
        self.block: Block = Block(layout=layout, border=border)
        self._current: Renderable = self.block

    # inspired by airium
    def __call__(self, thing: Renderable) -> ContextManager[None]:
        self._current.add(thing)

        @contextmanager
        def ctx() -> Iterator[None]:
            last = self._current
            self._current = thing
            yield
            self._current = last

        return ctx()

    def add(self, thing: Renderable):
        self.block.add(thing)

    def render(self):
        w("\x1b[2J")
        render_table = RenderTable()
        self.block.size(render_table)
        self.block.place(render_table)
        for span in self.block.render(render_table):
            for dx, ch in enumerate(span.text):
                w(cursor_to(span.pos + Vec(dx, 0)))
                w(
                    f"{span.style.fg_color.ansi_fg}{span.style.bg_color.ansi_bg}{ch}\x1b[0m"
                )
        f()


def tag_to_color(tag):
    match tag:
        case "blue":
            return Color.BLUE

        case "cyan":
            return Color.CYAN

        case "red":
            return Color.RED

        case "yellow":
            return Color.YELLOW

        case "green":
            return Color.GREEN

        case _:
            return Color.NONE


def is_valid_tag(tag):
    return tag_to_color(tag) is not Color.NONE


def resolve_markup(markup: str) -> Iterator[Span]:
    extract_text = re.compile(r"(?P<text>([^\[]|\[\[)*)(?P<rest>.*)")
    extract_tag = re.compile(r"\[(?P<tag>[^\]]*)\](?P<rest>.*)")

    pos = 0
    tag_stack = []
    s = markup
    while s:
        m = extract_text.match(s)
        assert m is not None, f"invalid markup: '{markup}'"
        text = m.group("text")
        if text:
            if tag_stack:
                yield Span(
                    Vec(pos, 0),
                    text,
                    Style(fg_color=tag_to_color(tag_stack[-1])),
                )
            else:
                yield Span(Vec(pos, 0), text)
            pos += len(text)
        s = m.group("rest")
        if s:
            m = extract_tag.match(s)
            assert m is not None, f"invalid markup: '{markup}'"
            tag = m.group("tag")
            if tag:
                if tag.startswith("/"):
                    assert tag[1:] in ["", tag_stack[-1]]
                    tag_stack.pop(-1)
                else:
                    assert is_valid_tag(tag), f"invalid tag: {tag}"
                    tag_stack.append(tag)
            s = m.group("rest")
    assert not tag_stack, f"unclosed tags: {', '.join(tag_stack)} in '{markup}'"


def len_markup(markup: str) -> int:
    extract_text = re.compile(r"(?P<text>([^\[]|\[\[)*)(?P<rest>.*)")
    extract_tag = re.compile(r"\[(?P<tag>[^\]]*)\](?P<rest>.*)")

    l = 0
    tag_stack = []
    s = markup
    while s:
        m = extract_text.match(s)
        assert m is not None, f"invalid markup: '{markup}'"
        text = m.group("text")
        if text:
            l += len(text)
        s = m.group("rest")
        if s:
            m = extract_tag.match(s)
            assert m is not None, f"invalid markup: '{markup}'"
            tag = m.group("tag")
            if tag:
                if tag.startswith("/"):
                    assert tag[1:] in ["", tag_stack[-1]]
                    tag_stack.pop(-1)
                else:
                    assert is_valid_tag(tag), f"invalid tag: {tag}"
                    tag_stack.append(tag)
            s = m.group("rest")
    assert not tag_stack, f"unclosed tags: {', '.join(tag_stack)} in '{markup}'"
    return l


class Text(Renderable):
    def __init__(self, text: str | Ref[str]):
        super().__init__()
        self.text: Ref[str] = Ref.of(text)

    @override
    def size(self, render_table: RenderTable):
        render_table[self].dim = Dim(len_markup(self.text.value), 1)

    @override
    def place(self, render_table: RenderTable):
        pass

    @override
    def render(self, render_table: RenderTable) -> Iterator[Span]:
        # yield Span(Vec(0, 0), self.text.value)
        yield from resolve_markup(self.text.value)
