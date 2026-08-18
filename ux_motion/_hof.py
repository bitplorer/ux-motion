"""Drop-in higher-order motion. Always return a live Scene.

Patterns in ``_patterns.py`` take selectors and return frozen plans.
These take ux-dom trees (or selectors) and stay in BUILD — serialize
happens at ``.play()`` / ``dumps`` / ``Scene.__render__``.

    from ux_motion import appear, swap, rise

    appear(section(h1("Shop"), id="view")).play()
    swap("#view", shop_view(), stagger=".tile").play()
    rise(product_view(), stagger=".tile")          # family as HOF
"""

from __future__ import annotations

from typing import Any, Callable, Mapping

from ux_motion._api import Scene, cue, scene, track, wait
from ux_motion._ir import PlanError
from ux_motion._recipes import Recipe, fade, none, rise, scale, slide
from ux_motion._tokens import tokens


def css_target(node: Any) -> str:
    """CSS selector for a tree, string, or ``#id``.

    ``section(..., id="view")`` → ``#view``.
    ``"view"`` / ``"#view"`` / ``".tile"`` pass through (bare words get ``#``).
    """
    if node is None:
        raise PlanError("css_target: nothing to select")
    if isinstance(node, str):
        text = node.strip()
        if not text:
            raise PlanError("css_target: empty string")
        if text[0] in ".#[:*":
            return text
        return f"#{text}"
    uid = _attr(node, "id")
    if uid:
        return f"#{uid}"
    for child in _children(node):
        try:
            return css_target(child)
        except PlanError:
            continue
    raise PlanError("css_target: no id on tree; pass into= or set id=")


def _attr(node: Any, key: str) -> Any:
    attrs = getattr(node, "attributes", None)
    if isinstance(attrs, Mapping):
        return attrs.get(key)
    return None


def _children(node: Any) -> list[Any]:
    kids = getattr(node, "children", None)
    return list(kids) if isinstance(kids, (list, tuple)) else []


def _find_id(node: Any, *, prefix: str | None = None, cls: str | None = None) -> str | None:
    uid = _attr(node, "id")
    klass = str(_attr(node, "class") or "")
    classes = klass.split()
    if uid:
        ok_prefix = prefix is None or str(uid).startswith(prefix)
        ok_cls = cls is None or cls in classes
        if ok_prefix and ok_cls:
            return f"#{uid}"
    for child in _children(node):
        found = _find_id(child, prefix=prefix, cls=cls)
        if found:
            return found
    return None


def _sel_html(value: Any) -> tuple[str, Any | None]:
    """``(selector, html_or_None)``. Strings are selectors only."""
    if value is None:
        raise PlanError("expected a tree or selector")
    if isinstance(value, str):
        return css_target(value), None
    return css_target(value), value


def _as_recipe(using: Any, *, role: str = "enter") -> Mapping[str, Any]:
    if using is None:
        using = rise if role == "enter" else fade
    enter = getattr(using, "enter", None)
    exit_ = getattr(using, "exit", None)
    if role == "exit" and callable(exit_) and not isinstance(using, Mapping):
        return exit_()
    if role != "exit" and callable(enter) and not isinstance(using, Mapping):
        return enter()
    if not isinstance(using, Mapping):
        raise PlanError("using= must be a Recipe or a family (rise/fade/…)")
    return using


def _child_selector(host: str, children: str) -> str:
    text = children.strip()
    if not text:
        raise PlanError("stagger selector is empty")
    if text.startswith(host) or text.startswith("#"):
        return text
    return f"{host} {text}"


def _apply_share(builder: Scene, share: Any) -> None:
    if share is None:
        return
    if isinstance(share, str):
        builder.share(share, leave=f"#thumb-{share}", arrive=f"#hero-{share}")
        return
    if isinstance(share, (tuple, list)) and len(share) == 3:
        builder.share(str(share[0]), leave=str(share[1]), arrive=str(share[2]))
        return
    raise PlanError("share= must be an id string or (id, leave, arrive)")


def appear(
    tree: Any = None,
    /,
    *,
    into: str | None = None,
    using: Any = None,
    stagger: str | None = None,
    gap_ms: int | None = None,
    name: str = "appear",
) -> Scene:
    """Enter a tree. Target is ``into`` or the tree's ``id``.

    ``html=`` stays the live tree until the wire.
    """
    if tree is None and into is None:
        raise PlanError("appear() needs a tree or into=")
    if into is not None:
        target = css_target(into)
        html = tree
    else:
        target, html = _sel_html(tree)
    rec = _as_recipe(using, role="enter")
    builder = scene(name).enter(target, rec, html=html)
    if stagger:
        builder.stagger_in(
            _child_selector(target, stagger),
            rise.enter(ms=tokens.ms("enter")),
            gap_ms=gap_ms if gap_ms is not None else tokens.ms("stagger"),
        )
    return builder


def leave(
    target: Any,
    /,
    *,
    using: Any = None,
    after: str = "hide",
    name: str = "leave",
) -> Scene:
    """Exit a host (selector or tree)."""
    sel, html = _sel_html(target) if not isinstance(target, str) else (css_target(target), None)
    rec = _as_recipe(using, role="exit")
    return scene(name).exit(sel, rec, after=after, html=html)


def swap(
    host: Any,
    tree: Any,
    /,
    *,
    using: Any = None,
    stagger: str | None = None,
    gap_ms: int | None = None,
    share: Any = None,
    name: str = "swap",
) -> Scene:
    """Replace ``host`` with ``tree`` (page change). Optional stagger + FLIP share."""
    target = css_target(host)
    rec = _as_recipe(using, role="enter")
    builder = scene(name)
    _apply_share(builder, share)
    builder.enter(target, rec, html=tree)
    if stagger:
        builder.stagger_in(
            _child_selector(target, stagger),
            rise.enter(ms=tokens.ms("enter")),
            gap_ms=gap_ms if gap_ms is not None else tokens.ms("stagger"),
        )
    return builder


def sheet(
    overlay: Any,
    panel: Any = "#sheet-panel",
    /,
    *,
    open_: bool = True,
    name: str = "sheet",
) -> Scene:
    """Modal: overlay fade + panel scale. Overlay/panel may be trees."""
    ov_sel, ov_html = _sel_html(overlay)
    pn_sel, pn_html = _sel_html(panel)
    builder = scene(name).parallel()
    if open_:
        builder.enter(ov_sel, fade.enter(ms=tokens.ms("fast")), html=ov_html)
        builder.enter(pn_sel, scale.enter(ms=tokens.ms("modal")), html=pn_html)
    else:
        builder.exit(pn_sel, scale.exit(ms=tokens.ms("fast")), after="hide")
        builder.exit(ov_sel, fade.exit(ms=tokens.ms("exit")), after="hide")
    return builder


def notice(
    tree: Any,
    /,
    *,
    show: bool = True,
    name: str = "notice",
) -> Scene:
    """Toast. Animates the inner ``#toast-*`` (or the tree's own id)."""
    inner = None
    html = None
    if isinstance(tree, str):
        inner = css_target(tree)
    else:
        html = tree
        inner = _find_id(tree, prefix="toast-") or _find_id(tree, cls="toast")
        if inner is None:
            inner = css_target(tree)
    rec_in = slide.enter(y=-tokens.dist("sm"), ms=tokens.ms("enter"))
    rec_out = slide.exit(y=-tokens.dist("sm"), ms=tokens.ms("fast"))
    builder = scene(name)
    if show:
        builder.enter(inner, rec_in, html=html)
    else:
        builder.exit(inner, rec_out, after="remove")
    return builder


def staggered(
    host: Any,
    children: str = ".tile",
    /,
    *,
    using: Any = None,
    gap_ms: int | None = None,
    enter: bool = True,
    name: str = "list",
) -> Scene:
    """Stagger children of a host (tree or selector). Host html is kept if given."""
    if isinstance(host, str):
        target = css_target(host)
        html = None
    else:
        target, html = _sel_html(host)
    sel = _child_selector(target, children)
    rec = _as_recipe(using, role="enter" if enter else "exit")
    gap = gap_ms if gap_ms is not None else tokens.ms("stagger")
    builder = scene(name)
    if html is not None:
        builder.enter(target, none() if enter else fade.exit(ms=0), html=html)
    if enter:
        builder.stagger_in(sel, rec, gap_ms=gap)
    else:
        builder.stagger_out(sel, rec, gap_ms=max(gap // 2, 10))
    return builder


def hop_leave(
    score_id: str,
    target: Any,
    /,
    *,
    using: Any = None,
    name: str = "hop-leave",
) -> Scene:
    """First Result of a multi-hop: exit and hold under a score."""
    sel, html = _sel_html(target) if not isinstance(target, str) else (css_target(target), None)
    rec = _as_recipe(using, role="exit")
    return scene(name).as_score(score_id, phase="hold").exit(sel, rec, after="keep", html=html)


def hop_arrive(
    score_id: str,
    target: Any,
    /,
    *,
    using: Any = None,
    name: str = "hop-arrive",
) -> Scene:
    """Second Result of a multi-hop: cue the score and enter."""
    sel, html = _sel_html(target) if not isinstance(target, str) else (css_target(target), None)
    rec = _as_recipe(using, role="enter")
    body = wait(cue(score_id), track(sel, rec, role="enter", after="keep", html=html))
    return scene(name).also(body)


class _Hop:
    leave = staticmethod(hop_leave)
    arrive = staticmethod(hop_arrive)


hop = _Hop()


def motion(
    fn: Callable[..., Any] | None = None,
    /,
    *,
    into: str | None = None,
    using: Any = None,
    stagger: str | None = None,
    name: str | None = None,
) -> Any:
    """Decorator: view function → Scene.

    Keep raw views undecorated if they also render into a Document.
    ``fn.view`` is the original callable.
    """

    def bind(func: Callable[..., Any]) -> Callable[..., Scene]:
        def wrapped(*args: Any, **kwargs: Any) -> Scene:
            tree = func(*args, **kwargs)
            return appear(
                tree,
                into=into,
                using=using,
                stagger=stagger,
                name=name or getattr(func, "__name__", "appear"),
            )

        wrapped.__name__ = getattr(func, "__name__", "motion")
        wrapped.__wrapped__ = func  # type: ignore[attr-defined]
        wrapped.view = func  # type: ignore[attr-defined]
        return wrapped

    if fn is not None:
        return bind(fn)
    return bind


def apply_family(
    family: Any,
    node: Any = None,
    /,
    *,
    into: str | None = None,
    stagger: str | None = None,
    gap_ms: int | None = None,
    after: str = "keep",
    role: str = "enter",
    name: str | None = None,
    **recipe_kw: Any,
) -> Scene | Recipe:
    """``rise(tree)`` → Scene. ``rise()`` / ``rise(ms=180)`` → Recipe."""
    rec = family.exit(**recipe_kw) if role == "exit" else family.enter(**recipe_kw)
    if node is None and into is None:
        return rec
    if role == "exit":
        return leave(node if node is not None else into, using=rec, after=after, name=name or family.name)
    return appear(
        node,
        into=into,
        using=rec,
        stagger=stagger,
        gap_ms=gap_ms,
        name=name or family.name,
    )


HOFS = {
    "appear": appear,
    "leave": leave,
    "swap": swap,
    "sheet": sheet,
    "notice": notice,
    "staggered": staggered,
    "hop": hop,
    "motion": motion,
}
