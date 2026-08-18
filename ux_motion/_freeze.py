"""Freeze an authoring plan into wire IR (all html fields are strings).

BUILD keeps ux-dom trees on ``track.html``. SERIALIZE walks those fields
through official ``render_markup`` (HTMLResponse's ``__render__`` path)
and then validates the string-only IR the player understands.
"""

from __future__ import annotations

from typing import Any, Iterator, Mapping

from ux_motion._ir import (
    KIND_BIND,
    KIND_CUE,
    KIND_GROUP,
    KIND_PHASE,
    KIND_PLAN,
    KIND_SCORE,
    validate_plan,
)
from ux_motion._render import is_renderable, render_markup


def _freeze_html(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return render_markup(value)
    return render_markup(value)


def _freeze_node(node: Any) -> Any:
    if not isinstance(node, Mapping):
        return node
    out = dict(node)
    html = out.get("html")
    if html is not None and not isinstance(html, str):
        out["html"] = _freeze_html(html)
    elif isinstance(html, str):
        out["html"] = render_markup(html)
    child = out.get("child")
    if isinstance(child, Mapping):
        out["child"] = _freeze_node(child)
    for key in ("children", "tracks"):
        seq = out.get(key)
        if isinstance(seq, list):
            out[key] = [_freeze_node(item) for item in seq]
    return out


def freeze_plan(plan: Mapping[str, Any] | Any) -> dict[str, Any]:
    """Serialize every ``html`` field, then validate the wire IR.

    Accepts a plan dict, or any object with ``.plan()`` (a ``Scene``).
    Does not mutate the authoring plan — trees stay on the builder.
    """
    if not isinstance(plan, Mapping) and hasattr(plan, "plan"):
        plan = plan.plan()
    if not isinstance(plan, Mapping):
        raise TypeError(f"freeze_plan expected a plan mapping, got {type(plan)!r}")
    raw = dict(plan)
    if raw.get("kind") == KIND_PLAN or "root" in raw:
        if "root" in raw:
            raw["root"] = _freeze_node(raw["root"])
        if "reduce_tree" in raw:
            raw["reduce_tree"] = _freeze_node(raw["reduce_tree"])
        return validate_plan(raw)
    return validate_plan(_freeze_node(raw))


def iter_markup(plan: Mapping[str, Any] | Any) -> Iterator[Any]:
    """Yield live ``html`` values (trees or strings) still on the authoring plan."""
    if not isinstance(plan, Mapping) and hasattr(plan, "plan"):
        plan = plan.plan()
    if not isinstance(plan, Mapping):
        return
    stack: list[Any] = [plan.get("root", plan)]
    if plan.get("reduce_tree") is not None:
        stack.append(plan["reduce_tree"])
    while stack:
        node = stack.pop()
        if not isinstance(node, Mapping):
            continue
        html = node.get("html")
        if html is not None:
            yield html
        child = node.get("child")
        if isinstance(child, Mapping):
            stack.append(child)
        for key in ("children", "tracks"):
            seq = node.get(key)
            if isinstance(seq, list):
                stack.extend(seq)


def plan_has_trees(plan: Mapping[str, Any] | Any) -> bool:
    return any(is_renderable(html) for html in iter_markup(plan))
