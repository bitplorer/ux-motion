"""Public alias for official serialize.

``as_html`` used to coerce at ``enter()``. That was the wrong phase.
Trees stay trees through BUILD. ``as_html`` is now ``render_markup`` —
the same ``stamp_tree`` + ``__render__`` sequence HTMLResponse uses —
and is only called at the wire (``dumps`` / ``send.play`` / ``Scene.__render__``).
"""

from __future__ import annotations

from ux_motion._render import render_markup

as_html = render_markup

__all__ = ["as_html", "render_markup"]
