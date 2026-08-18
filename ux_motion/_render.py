"""Official serialize — the same path ux-dom uses on the wire.

ux-dom has two phases (see ux-dom RENDER_PHASES):

    BUILD      Component.render() / tag constructors
    SERIALIZE  stamp_tree (CSP nonce) then ``__render__`` / ``_walk_render_tokens``

Every host wire ends there:

    HTMLResponse.render      → stamp_tree → content.__render__()
    StreamingResponse        → stamp_tree → __async_render__(pretty=False)
    str(tag)                 → __render__()
    Channel UxDomRenderer    → value.__render__()

Motion must not invent a second stringify. ``render_markup`` *is* that
sequence, duck-typed so ux-dom stays an optional peer. Call it only at
the serialize / wire boundary — never at ``enter()`` / ``track()``.
"""

from __future__ import annotations

from typing import Any


def _stamp_if_nonce(node: Any) -> Any:
    """Bake a request CSP nonce the same way HTMLResponse does.

    No-ops when ux-dom is absent or no nonce is on the request Context.
    """
    try:
        from ux_dom.plugins.csp import resolve_nonce, stamp_nonce, stamp_tree
    except Exception:
        return node
    try:
        nonce = resolve_nonce()
    except Exception:
        return node
    if not nonce:
        return node
    if isinstance(node, str):
        try:
            return stamp_nonce([node])[0]
        except Exception:
            return node
    try:
        stamp_tree(node, nonce)
    except Exception:
        return node
    return node


def render_markup(node: Any, *, pretty: bool = False) -> str:
    """Serialize a ux-dom tree (or any renderable) the official way.

    1. ``stamp_tree`` / ``stamp_nonce`` if a CSP nonce is active
    2. ``node.__render__(pretty=…)`` — the same method HTMLResponse calls
    3. ``node.__html__()`` (MarkupSafe / Channel SafeHtml)
    4. ``str`` / ``bytes`` pass through

    This is serialize, not build. Authoring code should keep the tree.
    """
    if node is None:
        return ""
    if isinstance(node, bytes):
        node = node.decode("utf-8")
    if isinstance(node, str):
        return _stamp_if_nonce(node)

    _stamp_if_nonce(node)

    render = getattr(node, "__render__", None)
    if callable(render):
        try:
            out = render(pretty=pretty)
        except TypeError:
            out = render()
        if out is None:
            return ""
        if isinstance(out, bytes):
            return out.decode("utf-8")
        if isinstance(out, str):
            return out
        node = out

    html = getattr(node, "__html__", None)
    if callable(html):
        return str(html())

    return str(node)


def is_renderable(value: Any) -> bool:
    """True when ``value`` can go through ``render_markup`` (not yet a string)."""
    if value is None or isinstance(value, (str, bytes)):
        return False
    return callable(getattr(value, "__render__", None)) or callable(
        getattr(value, "__html__", None)
    )
