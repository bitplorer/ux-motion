"""Fluent builders. These are the only objects product code should hold."""

from __future__ import annotations

from typing import Any, Iterable, Mapping, Sequence
from uuid import uuid4

from ux_motion._adapter import send
from ux_motion._compile import compile_plan
from ux_motion._ir import (
    KIND_BIND,
    KIND_CUE,
    KIND_GROUP,
    KIND_PHASE,
    KIND_SCORE,
    KIND_SHARE,
    KIND_STAGGER,
    KIND_TRACK,
    PlanError,
)
from ux_motion._markup import as_html
from ux_motion._ops import cancel as emit_cancel
from ux_motion._ops import play as emit_play
from ux_motion._ops import rewind_plan
from ux_motion._recipes import Recipe


def _as_recipe(recipe: Mapping[str, Any] | Recipe) -> dict[str, Any]:
    if not isinstance(recipe, Mapping):
        raise PlanError("recipe must be a mapping")
    return dict(recipe)


def _as_markup(html: Any) -> Any | None:
    """Keep trees as trees. Strings pass through. Nothing is serialized here."""
    if html is None:
        return None
    return html


def track(
    target: str,
    recipe: Mapping[str, Any],
    *,
    role: str = "enter",
    after: str | None = None,
    html: Any = None,
    name: str | None = None,
) -> dict[str, Any]:
    node: dict[str, Any] = {
        "kind": KIND_TRACK,
        "target": target,
        "role": role,
        "recipe": _as_recipe(recipe),
    }
    if after is not None:
        node["after"] = after
    elif role == "exit":
        node["after"] = "remove"
    else:
        node["after"] = "keep"
    markup = _as_markup(html)
    if markup is not None:
        node["html"] = markup
    if name:
        node["name"] = name
    return node


def stagger(
    selector: str,
    recipe: Mapping[str, Any],
    *,
    role: str = "enter",
    gap_ms: int = 40,
    after: str = "keep",
) -> dict[str, Any]:
    return {
        "kind": KIND_STAGGER,
        "selector": selector,
        "role": role,
        "gap_ms": int(gap_ms),
        "recipe": _as_recipe(recipe),
        "after": after,
    }


def share(
    sid: str,
    *,
    leave: str,
    arrive: str,
    recipe: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Named identity continuity. Client measures leave→arrive (FLIP)."""
    node: dict[str, Any] = {
        "kind": KIND_SHARE,
        "id": sid,
        "leave": leave,
        "arrive": arrive,
    }
    if recipe is not None:
        node["recipe"] = _as_recipe(recipe)
    return node


def bind(
    input_name: str,
    target: str,
    child: Mapping[str, Any],
    *,
    until: str | None = None,
    axis: str | None = None,
) -> dict[str, Any]:
    """Turn a subtree into a 0..1 tape driven by scroll, drag, or progress."""
    node: dict[str, Any] = {
        "kind": KIND_BIND,
        "input": input_name,
        "target": target,
        "child": dict(child),
    }
    if until:
        node["until"] = until
    if axis:
        node["axis"] = axis
    return node


def score(sid: str, child: Mapping[str, Any], *, phase: str = "now") -> dict[str, Any]:
    """Hold presence across HTTP Results until a matching cue arrives."""
    return {"kind": KIND_SCORE, "id": sid, "phase": phase, "child": dict(child)}


def cue(score_id: str, child: Mapping[str, Any] | None = None) -> dict[str, Any]:
    """Resolve a held score — typically the enter half of a multi-hop transition."""
    node: dict[str, Any] = {"kind": KIND_CUE, "score": score_id}
    if child is not None:
        node["child"] = dict(child)
    return node


def group(
    name: str,
    *children: Mapping[str, Any],
    mode: str = "wait",
    tracks: Sequence[Mapping[str, Any]] | None = None,
) -> dict[str, Any]:
    items = list(tracks) if tracks is not None else list(children)
    return {"kind": KIND_GROUP, "name": name, "mode": mode, "tracks": [dict(c) for c in items]}


def _phase(mode: str, children: Iterable[Mapping[str, Any]], stagger_ms: int = 0) -> dict[str, Any]:
    kids = [dict(c) for c in children]
    if not kids:
        raise PlanError("phase requires at least one child")
    return {"kind": KIND_PHASE, "mode": mode, "stagger_ms": int(stagger_ms), "children": kids}


def parallel(*children: Mapping[str, Any], stagger_ms: int = 0) -> dict[str, Any]:
    return _phase("parallel", children, stagger_ms)


def sequence(*children: Mapping[str, Any]) -> dict[str, Any]:
    return _phase("sequence", children)


def wait(*children: Mapping[str, Any]) -> dict[str, Any]:
    """Direct exit tracks finish before direct enter tracks. Nested groups stay independent."""
    return _phase("wait", children)


class Scene:
    """Composable scene. Internals may change; method names are frozen."""

    def __init__(self, sid: str | None = None) -> None:
        self._id = sid or f"scene-{uuid4().hex[:10]}"
        self._interrupt = "replace"
        self._reduced = "simplify"
        self._engine = "presence"
        self._mode = "wait"
        self._complete: str | None = None
        self._nodes: list[dict[str, Any]] = []
        self._open_group: str | None = None
        self._group_mode = "wait"
        self._pending: list[dict[str, Any]] = []
        self._reduce_tree: dict[str, Any] | None = None
        self._bind: dict[str, Any] | None = None
        self._score_id: str | None = None
        self._score_phase = "now"

    def interrupt(self, policy: str) -> "Scene":
        self._interrupt = policy
        return self

    def reduced(self, policy: str) -> "Scene":
        self._reduced = policy
        return self

    def engine(self, name: str) -> "Scene":
        self._engine = name
        return self

    def on_complete(self, action: str) -> "Scene":
        self._complete = action
        return self

    def when_reduce(self, *nodes: Mapping[str, Any]) -> "Scene":
        """Alternate tree for reduced motion when reduced='swap'."""
        self._reduce_tree = _phase("parallel", nodes) if len(nodes) > 1 else dict(nodes[0])
        self._reduced = "swap"
        return self

    def wait(self) -> "Scene":
        self._flush_group()
        self._mode = "wait"
        return self

    def parallel(self) -> "Scene":
        self._flush_group()
        self._mode = "parallel"
        return self

    def sequence(self) -> "Scene":
        self._flush_group()
        self._mode = "sequence"
        return self

    def also(self, *nodes: Mapping[str, Any]) -> "Scene":
        self._flush_group()
        self._nodes.extend(dict(n) for n in nodes)
        return self

    def named(self, name: str, mode: str = "wait") -> "Scene":
        self._flush_group()
        self._open_group = name
        self._group_mode = mode
        self._pending = []
        return self

    def exit(
        self,
        target: str,
        recipe: Mapping[str, Any],
        *,
        after: str = "remove",
        html: Any = None,
    ) -> "Scene":
        self._add(track(target, recipe, role="exit", after=after, html=html))
        return self

    def enter(
        self,
        target: str,
        recipe: Mapping[str, Any],
        *,
        after: str = "keep",
        html: Any = None,
    ) -> "Scene":
        """``html`` stays a ux-dom tree until official serialize (``__render__`` / wire)."""
        self._add(track(target, recipe, role="enter", after=after, html=html))
        return self

    def stay(self, target: str, recipe: Mapping[str, Any]) -> "Scene":
        self._add(track(target, recipe, role="stay", after="keep"))
        return self

    def stagger_in(self, selector: str, recipe: Mapping[str, Any], *, gap_ms: int = 40) -> "Scene":
        self._add(stagger(selector, recipe, role="enter", gap_ms=gap_ms))
        return self

    def stagger_out(self, selector: str, recipe: Mapping[str, Any], *, gap_ms: int = 30) -> "Scene":
        self._add(stagger(selector, recipe, role="exit", gap_ms=gap_ms, after="keep"))
        return self

    def share(
        self,
        sid: str,
        *,
        leave: str,
        arrive: str,
        recipe: Mapping[str, Any] | None = None,
    ) -> "Scene":
        self._add(share(sid, leave=leave, arrive=arrive, recipe=recipe))
        return self

    def bind_to(
        self,
        input_name: str,
        target: str,
        *,
        until: str | None = None,
        axis: str | None = None,
    ) -> "Scene":
        """Mark this whole scene as a scrubbable tape."""
        self._bind = {"input": input_name, "target": target, "until": until, "axis": axis}
        return self

    def as_score(self, sid: str, *, phase: str = "now") -> "Scene":
        self._score_id = sid
        self._score_phase = phase
        return self

    def _add(self, node: dict[str, Any]) -> None:
        if self._open_group is not None:
            self._pending.append(node)
        else:
            self._nodes.append(node)

    def _flush_group(self) -> None:
        if self._open_group is None:
            return
        if self._pending:
            self._nodes.append(group(self._open_group, *self._pending, mode=self._group_mode))
        self._open_group = None
        self._pending = []

    def iter_markup(self):
        """Live ``html`` values still on this scene (trees or strings)."""
        from ux_motion._freeze import iter_markup as _iter

        return _iter(self.plan())

    def tag(self):
        """ux-dom Component face so ``div(scene)`` / ``document`` accept this scene.

        The face serializes through official ``__render__`` (script with the
        full frozen plan). Html trees are not re-parented; ``render_markup``
        stamps them the same way HTMLResponse does.
        """
        n = len(self._nodes) + len(self._pending)
        face = getattr(self, "_tag_face", None)
        if face is None or getattr(self, "_tag_gen", None) != n:
            from ux_motion._dom import motion_tag

            face = motion_tag(self)
            self._tag_face = face
            self._tag_gen = n
        return face

    def __iter__(self):
        """Flatten into a ux-dom Component so ``dom_tag.add`` accepts a Scene.

        ux-dom ``_add_unlocked`` only takes tags / strings / iterables. Yielding
        the Component face lets ``div(scene)`` work without patching ux-dom.
        """
        yield self.tag()

    def __render__(self, indent: str = "  ", pretty: bool = True, xhtml: bool = False) -> str:
        """Official serialize — same method HTMLResponse / UxDomRenderer call.

        Freezes html trees through ``__render__``, then emits a script tag
        carrying the full plan (markup + recipes + identity). Nothing is lost.
        """
        from ux_motion._freeze import freeze_plan
        from ux_motion._wire import encode_plan_script

        return encode_plan_script(freeze_plan(self), pretty=pretty)

    def __html__(self) -> str:
        return self.__render__(pretty=False)

    def __str__(self) -> str:
        return self.__render__(pretty=False)

    def __repr__(self) -> str:
        return f"Scene(id={self._id!r}, mode={self._mode!r}, parts={len(self._nodes)})"

    def plan(self) -> dict[str, Any]:
        self._flush_group()
        if not self._nodes:
            raise PlanError("scene has no tracks")
        root: dict[str, Any] = _phase(self._mode, self._nodes)
        if self._bind is not None:
            root = {
                "kind": KIND_BIND,
                "input": self._bind["input"],
                "target": self._bind["target"],
                "child": root,
            }
            if self._bind.get("until"):
                root["until"] = self._bind["until"]
            if self._bind.get("axis"):
                root["axis"] = self._bind["axis"]
        if self._score_id is not None:
            root = {
                "kind": KIND_SCORE,
                "id": self._score_id,
                "phase": self._score_phase,
                "child": root,
            }
        raw: dict[str, Any] = {
            "v": "1",
            "kind": "plan",
            "id": self._id,
            "interrupt": self._interrupt,
            "reduced": self._reduced,
            "engine": self._engine,
            "root": root,
        }
        if self._complete:
            raw["complete"] = self._complete
        if self._reduce_tree is not None:
            raw["reduce_tree"] = self._reduce_tree
        return compile_plan(raw)

    def ops(self) -> list[dict[str, Any]]:
        return emit_play(self.plan())

    def play(self, *, also_update: bool = False, action: str | None = None) -> dict[str, Any]:
        return send.play(self.plan(), also_update=also_update, action=action)

    def update(self, *, action: str | None = None) -> dict[str, Any]:
        return send.update(self.plan(), action=action)

    def rewind(self, *, action: str | None = None) -> dict[str, Any]:
        return send.rewind(self.plan(), action=action)

    def cancel_ops(self) -> list[dict[str, Any]]:
        return emit_cancel(self._id)


def scene(sid: str | None = None) -> Scene:
    return Scene(sid)


class Motion:
    """Document runtime + namespace facade.

    ``document.use(Motion())`` injects the player the same way
    ``document.use(XElement())`` injects ``x_element.js``.

    ``Motion.scene`` / ``Motion.track`` stay as the fluent namespace.
    """

    plugin_kind = "contribution"
    name = "ux_motion"
    PLAYER_URL = "/ux-pkg/ux-motion/static/ux-motion-player.js"

    scene = staticmethod(scene)
    track = staticmethod(track)
    group = staticmethod(group)
    stagger = staticmethod(stagger)
    share = staticmethod(share)
    bind = staticmethod(bind)
    score = staticmethod(score)
    cue = staticmethod(cue)
    parallel = staticmethod(parallel)
    sequence = staticmethod(sequence)
    wait = staticmethod(wait)
    compile = staticmethod(compile_plan)
    play = staticmethod(send.play)
    update = staticmethod(send.update)
    rewind = staticmethod(send.rewind)
    cancel = staticmethod(emit_cancel)
    send = send
    as_html = staticmethod(as_html)

    def __init__(self, *, src: str | None = None, serve: str = "package_mount") -> None:
        self.serve = serve
        self.src = src or (
            self.PLAYER_URL if serve == "package_mount" else "/static/ux-motion-player.js"
        )

    def document_head(self):
        try:
            from ux_dom.dom import script
        except ImportError:
            return ()
        return (script(src=self.src, defer=True),)

    def document_body(self):
        return ()

    def served_files(self):
        if self.serve != "package_mount":
            return ()
        try:
            from ux_dom.plugins.safe_static import SafeStaticFile
        except ImportError:
            return ()
        return (
            SafeStaticFile.from_package(
                "ux_motion.scripts",
                "ux-motion-player.js",
                url=self.PLAYER_URL,
                plugin=self.name,
                content_type="application/javascript",
            ),
        )

    def artifacts(self):
        return ()
