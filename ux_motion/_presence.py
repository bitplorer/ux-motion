"""Presence helpers — stamp stable ids the player can hold across morphs."""

from __future__ import annotations

from html import escape
from typing import Iterable


def stamp(html: str, uid: str) -> str:
    """Inject data-uxm-id onto the first open tag."""
    safe = escape(uid, quote=True)
    marker = f' data-uxm-id="{safe}"'
    if not html or "<" not in html:
        return html
    i = html.find(">")
    if i < 0:
        return html
    # self-closing or normal
    if html[i - 1] == "/":
        return html[: i - 1] + marker + html[i - 1 :]
    return html[:i] + marker + html[i:]


def region(uid: str, body: str = "", *, cls: str = "", tag: str = "div") -> str:
    """A presence host with a stable id."""
    safe_id = escape(uid, quote=True)
    safe_cls = escape(cls, quote=True) if cls else ""
    class_attr = f' class="{safe_cls}"' if safe_cls else ""
    return f'<{tag} data-uxm-id="{safe_id}"{class_attr}>{body}</{tag}>'


class Presence:
    """Server-side presence map for tests and multi-hop scores."""

    def __init__(self) -> None:
        self._present: set[str] = set()

    def mark(self, uid: str) -> None:
        self._present.add(uid)

    def drop(self, uid: str) -> None:
        self._present.discard(uid)

    def is_present(self, uid: str) -> bool:
        return uid in self._present

    def clear(self) -> None:
        self._present.clear()

    def all(self) -> Iterable[str]:
        return sorted(self._present)
