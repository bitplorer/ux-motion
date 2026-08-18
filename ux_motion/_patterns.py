"""Full choreographies — not single recipes. Reusable presence patterns."""

from __future__ import annotations

from typing import Any, Mapping

from ux_motion._api import cue, score, wait
from ux_motion._api import scene as build_scene
from ux_motion._recipes import fade, rise, scale, slide
from ux_motion._tokens import tokens


def page(
    *,
    leave: str,
    arrive: str,
    name: str = "page",
    exit_ms: int | None = None,
    enter_ms: int | None = None,
) -> dict[str, Any]:
    """Classic page transition: exit old, then enter new."""
    return (
        build_scene(name)
        .exit(leave, fade.exit(ms=exit_ms or tokens.ms("exit")), after="hide")
        .enter(arrive, rise.enter(ms=enter_ms or tokens.ms("enter")))
        .plan()
    )


def modal(
    *,
    overlay: str,
    panel: str,
    name: str = "modal",
    open_: bool = True,
) -> dict[str, Any]:
    """Modal open/close with overlay fade + panel scale."""
    s = build_scene(name).parallel()
    if open_:
        s.enter(overlay, fade.enter(ms=tokens.ms("fast")))
        s.enter(panel, scale.enter(ms=tokens.ms("modal")))
    else:
        s.exit(panel, scale.exit(ms=tokens.ms("fast")), after="hide")
        s.exit(overlay, fade.exit(ms=tokens.ms("exit")), after="hide")
    return s.plan()


def toast(
    *,
    target: str,
    name: str = "toast",
    show: bool = True,
) -> dict[str, Any]:
    """Toast slide from the edge."""
    s = build_scene(name)
    if show:
        s.enter(target, slide.enter(y=-tokens.dist("sm"), ms=tokens.ms("enter")))
    else:
        s.exit(target, slide.exit(y=-tokens.dist("sm"), ms=tokens.ms("fast")), after="remove")
    return s.plan()


def list_stagger(
    *,
    selector: str,
    name: str = "list",
    enter: bool = True,
    gap_ms: int | None = None,
) -> dict[str, Any]:
    """Staggered list enter or exit."""
    s = build_scene(name)
    gap = gap_ms if gap_ms is not None else tokens.ms("stagger")
    if enter:
        s.stagger_in(selector, rise.enter(ms=tokens.ms("enter")), gap_ms=gap)
    else:
        s.stagger_out(selector, fade.exit(ms=tokens.ms("fast")), gap_ms=max(gap // 2, 10))
    return s.plan()


def shared_page(
    *,
    share_id: str,
    leave_img: str,
    arrive_img: str,
    leave_page: str,
    arrive_page: str,
    name: str = "shared-page",
) -> dict[str, Any]:
    """Page change with a shared hero element (FLIP)."""
    return (
        build_scene(name)
        .share(share_id, leave=leave_img, arrive=arrive_img)
        .exit(leave_page, fade.exit(ms=tokens.ms("exit")), after="hide")
        .enter(arrive_page, fade.enter(ms=tokens.ms("enter")))
        .plan()
    )


def multi_hop_leave(
    *,
    score_id: str,
    leave: str,
    name: str = "hop-leave",
) -> dict[str, Any]:
    """First Result of a multi-hop: exit and hold under a score."""
    return (
        build_scene(name)
        .as_score(score_id, phase="hold")
        .exit(leave, fade.exit(ms=tokens.ms("exit")), after="keep")
        .plan()
    )


def multi_hop_arrive(
    *,
    score_id: str,
    arrive: str,
    name: str = "hop-arrive",
) -> dict[str, Any]:
    """Second Result of a multi-hop: cue the score and enter."""
    body = wait(
        {"kind": "cue", "score": score_id},
        {"kind": "track", "target": arrive, "role": "enter", "after": "keep", "recipe": rise.enter()},
    )
    return build_scene(name).also(body).plan()


PATTERNS = {
    "page": page,
    "modal": modal,
    "toast": toast,
    "list": list_stagger,
    "shared_page": shared_page,
    "multi_hop_leave": multi_hop_leave,
    "multi_hop_arrive": multi_hop_arrive,
}
