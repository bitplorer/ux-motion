"""What a plan becomes on the wire.

play(plan)     → transition.play
as_update(plan)→ morph / remove / set_attr
rewind(plan)   → transition.rewind (inverted from/to)
"""

from __future__ import annotations

from typing import Any, Mapping, Sequence

from ux_motion._freeze import freeze_plan
from ux_motion._ir import (
    KIND_BIND,
    KIND_CUE,
    KIND_GROUP,
    KIND_PHASE,
    KIND_SCORE,
    KIND_SHARE,
    KIND_STAGGER,
    KIND_TRACK,
    validate_plan,
)

OP_PLAY = "transition.play"
OP_CANCEL = "transition.cancel"
OP_REWIND = "transition.rewind"


def _op(op_type: str, **fields: Any) -> dict[str, Any]:
    body: dict[str, Any] = {"op": op_type}
    for key, value in fields.items():
        if value is not None:
            body[key] = value
    return body


def play(plan: Mapping[str, Any], *, meta: Mapping[str, Any] | None = None) -> list[dict[str, Any]]:
    frozen = freeze_plan(plan)
    return [_op(OP_PLAY, plan=frozen, meta=dict(meta) if meta else None)]


def cancel(plan_id: str | None = None, *, meta: Mapping[str, Any] | None = None) -> list[dict[str, Any]]:
    return [_op(OP_CANCEL, id=plan_id, meta=dict(meta) if meta else None)]


def _invert_recipe(recipe: Mapping[str, Any]) -> dict[str, Any]:
    out = dict(recipe)
    frm = recipe.get("from")
    to = recipe.get("to")
    if frm is not None or to is not None:
        out["from"] = dict(to) if to else {}
        out["to"] = dict(frm) if frm else {}
    name = str(recipe.get("name") or "")
    if name.endswith(".enter"):
        out["name"] = name[: -len(".enter")] + ".exit"
    elif name.endswith(".exit"):
        out["name"] = name[: -len(".exit")] + ".enter"
    return out


def _invert_node(node: Mapping[str, Any]) -> dict[str, Any]:
    kind = node.get("kind")
    out = dict(node)
    if kind == KIND_TRACK:
        role = node.get("role")
        if role == "enter":
            out["role"] = "exit"
            out["after"] = node.get("after") if node.get("after") != "keep" else "remove"
        elif role == "exit":
            out["role"] = "enter"
            out["after"] = "keep"
        out["recipe"] = _invert_recipe(node.get("recipe") or {})
        return out
    if kind == KIND_STAGGER:
        role = node.get("role")
        out["role"] = "exit" if role == "enter" else "enter" if role == "exit" else role
        out["recipe"] = _invert_recipe(node.get("recipe") or {})
        return out
    if kind == KIND_GROUP:
        out["tracks"] = [_invert_node(c) for c in reversed(list(node.get("tracks") or []))]
        return out
    if kind == KIND_PHASE:
        out["children"] = [_invert_node(c) for c in reversed(list(node.get("children") or []))]
        return out
    if kind == KIND_SHARE:
        out["leave"], out["arrive"] = node.get("arrive"), node.get("leave")
        out["recipe"] = _invert_recipe(node.get("recipe") or {})
        return out
    if kind in {KIND_BIND, KIND_SCORE, KIND_CUE}:
        child = node.get("child")
        if child is not None:
            out["child"] = _invert_node(child)
        return out
    return out


def rewind_plan(plan: Mapping[str, Any]) -> dict[str, Any]:
    frozen = freeze_plan(plan)
    inverted = dict(frozen)
    inverted["id"] = f"{frozen['id']}__rewind"
    inverted["root"] = _invert_node(frozen["root"])
    return validate_plan(inverted)


def rewind(plan: Mapping[str, Any], *, meta: Mapping[str, Any] | None = None) -> list[dict[str, Any]]:
    inverted = rewind_plan(plan)
    return [_op(OP_REWIND, plan=inverted, meta=dict(meta) if meta else None)]


def to_result(
    ops: Sequence[Mapping[str, Any]],
    *,
    ok: bool = True,
    action: str | None = None,
) -> dict[str, Any]:
    result: dict[str, Any] = {"ok": ok, "ops": [dict(o) for o in ops]}
    if action:
        result["meta"] = {"action": action}
    return result


def _walk(node: Mapping[str, Any], acc: list[dict[str, Any]]) -> None:
    kind = node.get("kind")
    if kind in {KIND_TRACK, KIND_STAGGER, KIND_SHARE}:
        acc.append(dict(node))
        return
    if kind == KIND_GROUP:
        for child in node.get("tracks") or []:
            _walk(child, acc)
        return
    if kind == KIND_PHASE:
        for child in node.get("children") or []:
            _walk(child, acc)
        return
    if kind in {KIND_BIND, KIND_SCORE, KIND_CUE}:
        child = node.get("child")
        if child is not None:
            _walk(child, acc)


def as_update(plan: Mapping[str, Any]) -> list[dict[str, Any]]:
    """Same scene, no motion — just the DOM change."""
    frozen = freeze_plan(plan)
    tracks: list[dict[str, Any]] = []
    _walk(frozen["root"], tracks)
    ops: list[dict[str, Any]] = []
    for t in tracks:
        kind = t.get("kind")
        if kind == KIND_STAGGER:
            sel = t.get("selector")
            role = t.get("role")
            after = t.get("after")
            if role == "enter":
                ops.append(_op("set_attr", target=sel, attrs={"data-uxm-present": "1"}))
            elif role == "exit" and after == "remove":
                ops.append(_op("remove", target=sel))
            elif role == "exit" and after == "hide":
                ops.append(_op("set_attr", target=sel, attrs={"hidden": "true", "aria-hidden": "true"}))
            continue
        if kind == KIND_SHARE:
            # Shared element final state: show arrive, hide/remove leave.
            ops.append(_op("set_attr", target=t.get("arrive"), attrs={"data-uxm-share": t.get("id"), "data-uxm-present": "1"}))
            ops.append(_op("set_attr", target=t.get("leave"), attrs={"data-uxm-present": "0"}))
            continue
        role = t.get("role")
        target = t.get("target")
        html = t.get("html")
        after = t.get("after")
        if role == "enter" and html:
            ops.append(_op("morph", target=target, html=html, morph="idiomorph"))
        elif role == "exit" and after == "remove" and not html:
            ops.append(_op("remove", target=target))
        elif role == "enter" and not html:
            ops.append(_op("set_attr", target=target, attrs={"data-uxm-present": "1"}))
        elif role == "exit" and after == "hide":
            ops.append(_op("set_attr", target=target, attrs={"hidden": "true", "aria-hidden": "true"}))
    if not ops:
        ops.append(_op("noop", meta={"as": "update", "empty": True}))
    return ops
