"""Reference player — the decades contract.

The web player must produce the same start/end order for a given plan.
Time is discrete milliseconds. Nested groups are never flattened.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

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


@dataclass(frozen=True)
class Event:
    t: int
    event: str
    target: str
    role: str
    name: str = ""


def _emit_track(node: Mapping[str, Any], t0: int, events: list[Event], counts: Mapping[str, int]) -> int:
    kind = node["kind"]
    role = str(node.get("role") or "enter")
    recipe = node.get("recipe") or {}
    name = str(node.get("name") or recipe.get("name") or "")
    if kind == KIND_STAGGER:
        sel = str(node["selector"])
        n = int(counts.get(sel, 3))
        gap = int(node.get("gap_ms") or 40)
        end = t0
        for i in range(n):
            start = t0 + int(recipe.get("delay") or 0) + i * gap
            finish = start + int(recipe.get("duration") or 0)
            tgt = f"{sel}[{i}]"
            events.append(Event(start, "start", tgt, role, name))
            events.append(Event(finish, "end", tgt, role, name))
            end = max(end, finish)
        return end
    if kind == KIND_SHARE:
        duration = int(recipe.get("duration") or 320) + int(recipe.get("delay") or 0)
        leave = str(node["leave"])
        arrive = str(node["arrive"])
        sid = str(node["id"])
        events.append(Event(t0, "start", leave, "share-leave", sid))
        events.append(Event(t0, "start", arrive, "share-arrive", sid))
        events.append(Event(t0 + duration, "end", leave, "share-leave", sid))
        events.append(Event(t0 + duration, "end", arrive, "share-arrive", sid))
        return t0 + duration
    tgt = str(node.get("target") or "")
    start = t0 + int(recipe.get("delay") or 0)
    finish = start + int(recipe.get("duration") or 0)
    events.append(Event(start, "start", tgt, role, name))
    events.append(Event(finish, "end", tgt, role, name))
    return finish


def _play_node(node: Mapping[str, Any], t0: int, events: list[Event], counts: Mapping[str, int]) -> int:
    kind = node.get("kind")
    if kind in {KIND_TRACK, KIND_STAGGER, KIND_SHARE}:
        return _emit_track(node, t0, events, counts)
    if kind == KIND_GROUP:
        return _play_phase(
            {
                "kind": KIND_PHASE,
                "mode": node.get("mode") or "wait",
                "stagger_ms": 0,
                "children": node.get("tracks") or [],
            },
            t0,
            events,
            counts,
        )
    if kind == KIND_PHASE:
        return _play_phase(node, t0, events, counts)
    if kind in {KIND_BIND, KIND_SCORE, KIND_CUE}:
        child = node.get("child")
        if child is None:
            return t0
        # bind/score/cue wrap a child; schedule is the child's schedule from t0
        end = _play_node(child, t0, events, counts)
        label = str(node.get("id") or node.get("score") or node.get("target") or kind)
        events.append(Event(t0, "start", f"@{kind}:{label}", kind, label))
        events.append(Event(end, "end", f"@{kind}:{label}", kind, label))
        return end
    return t0


def _play_phase(phase: Mapping[str, Any], t0: int, events: list[Event], counts: Mapping[str, int]) -> int:
    kids = list(phase.get("children") or [])
    mode = phase.get("mode") or "parallel"
    stagger_ms = int(phase.get("stagger_ms") or 0)
    if not kids:
        return t0
    if mode == "sequence":
        t = t0
        for i, child in enumerate(kids):
            start = t
            if i and stagger_ms:
                start = t + stagger_ms
            t = _play_node(child, start, events, counts)
        return t
    if mode == "wait":
        exits: list[Mapping[str, Any]] = []
        stays: list[Mapping[str, Any]] = []
        enters: list[Mapping[str, Any]] = []
        nested: list[Mapping[str, Any]] = []
        for child in kids:
            k = child.get("kind")
            if k in {KIND_TRACK, KIND_STAGGER}:
                role = child.get("role") or "enter"
                if role == "exit":
                    exits.append(child)
                elif role == "enter":
                    enters.append(child)
                else:
                    stays.append(child)
            else:
                nested.append(child)
        exit_end = t0
        for child in exits:
            exit_end = max(exit_end, _play_node(child, t0, events, counts))
        stay_end = exit_end
        for child in stays:
            stay_end = max(stay_end, _play_node(child, exit_end, events, counts))
        nested_end = t0
        for child in nested:
            nested_end = max(nested_end, _play_node(child, t0, events, counts))
        enter_t = stay_end if (exits or stays) else t0
        enter_end = enter_t
        for child in enters:
            enter_end = max(enter_end, _play_node(child, enter_t, events, counts))
        return max(stay_end, nested_end, enter_end)
    end = t0
    for i, child in enumerate(kids):
        start = t0 + i * stagger_ms
        end = max(end, _play_node(child, start, events, counts))
    return end


def interpret(
    plan: Mapping[str, Any],
    *,
    counts: Mapping[str, int] | None = None,
) -> list[Event]:
    """Deterministic start/end schedule. Sorted by (t, event, target)."""
    frozen = validate_plan(plan)
    events: list[Event] = []
    _play_node(frozen["root"], 0, events, counts or {})
    events.sort(key=lambda e: (e.t, 0 if e.event == "start" else 1, e.target, e.role))
    return events


def span_ms(plan: Mapping[str, Any], *, counts: Mapping[str, int] | None = None) -> int:
    ev = interpret(plan, counts=counts)
    return max((e.t for e in ev), default=0)


def explain(plan: Mapping[str, Any], *, counts: Mapping[str, int] | None = None) -> str:
    """Human schedule. Same order as the reference player."""
    frozen = validate_plan(plan)
    lines = [
        f"plan {frozen['id']}  mode={frozen['root'].get('mode', frozen['root'].get('kind', ''))}  "
        f"interrupt={frozen['interrupt']}  engine={frozen['engine']}"
    ]
    for e in interpret(frozen, counts=counts):
        extra = f"  {e.name}" if e.name else ""
        lines.append(f"{e.t:>6}ms  {e.event:<5}  {e.role:<12}  {e.target}{extra}")
    return "\n".join(lines)


def frames(
    plan: Mapping[str, Any],
    *,
    width: int = 640,
    height: int = 120,
    counts: Mapping[str, int] | None = None,
) -> str:
    """Headless SVG schedule strip for CI / docs. No browser required."""
    frozen = validate_plan(plan)
    ev = interpret(frozen, counts=counts)
    total = max((e.t for e in ev), default=1) or 1
    pad = 24
    row_h = 18
    targets = []
    seen = set()
    for e in ev:
        if e.target not in seen:
            seen.add(e.target)
            targets.append(e.target)
    h = max(height, pad * 2 + len(targets) * row_h)
    bars = []
    colors = {
        "exit": "#e85d4c",
        "enter": "#3ecf8e",
        "stay": "#6b8afd",
        "layout": "#6b8afd",
        "share-leave": "#f0a030",
        "share-arrive": "#f0a030",
        "bind": "#a78bfa",
        "score": "#38bdf8",
        "cue": "#38bdf8",
        "stagger": "#3ecf8e",
    }
    for e in ev:
        if e.event != "start":
            continue
        end = next(
            (x.t for x in ev if x.event == "end" and x.target == e.target and x.role == e.role and x.t >= e.t),
            e.t + 1,
        )
        yi = targets.index(e.target)
        x1 = pad + (e.t / total) * (width - pad * 2)
        x2 = pad + (end / total) * (width - pad * 2)
        y = pad + yi * row_h
        fill = colors.get(e.role, "#888")
        bars.append(
            f'<rect x="{x1:.1f}" y="{y}" width="{max(x2 - x1, 2):.1f}" height="12" rx="2" fill="{fill}" opacity="0.85"/>'
        )
        bars.append(
            f'<text x="{x1:.1f}" y="{y - 2}" font-size="9" fill="#aaa" font-family="ui-monospace,monospace">{_xml(e.target)}</text>'
        )
    labels = [
        f'<text x="8" y="14" font-size="11" fill="#ccc" font-family="ui-monospace,monospace">plan { _xml(frozen["id"]) } · {total}ms</text>'
    ]
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{h}" viewBox="0 0 {width} {h}">'
        f'<rect width="100%" height="100%" fill="#0f1419"/>'
        + "".join(labels)
        + "".join(bars)
        + "</svg>"
    )


def _xml(s: str) -> str:
    return (
        s.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )
