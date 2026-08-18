"""Plan IR v1 — append-only data shapes.

Receivers MUST ignore unknown fields.
A new ``v`` is the only legal breaking change.
"""

from __future__ import annotations

from typing import Any, Mapping

from ux_motion._version import IR_VERSION  # noqa: E402 — single source

KIND_PLAN = "plan"
KIND_PHASE = "phase"
KIND_GROUP = "group"
KIND_TRACK = "track"
KIND_STAGGER = "stagger"
KIND_SHARE = "share"
KIND_BIND = "bind"
KIND_SCORE = "score"
KIND_CUE = "cue"

KINDS = frozenset(
    {
        KIND_PLAN,
        KIND_PHASE,
        KIND_GROUP,
        KIND_TRACK,
        KIND_STAGGER,
        KIND_SHARE,
        KIND_BIND,
        KIND_SCORE,
        KIND_CUE,
    }
)
MODES = frozenset({"parallel", "sequence", "wait"})
ROLES = frozenset({"exit", "enter", "stay", "layout"})
AFTERS = frozenset({"keep", "remove", "hide"})
INTERRUPTS = frozenset({"replace", "queue", "ignore"})
REDUCED = frozenset({"skip", "simplify", "honor", "swap"})
ENGINES = frozenset({"presence", "view", "spring"})
BIND_INPUTS = frozenset({"scroll", "drag", "progress"})
RECIPE_PROPS = frozenset({"opacity", "x", "y", "scale", "rotate", "blur", "offset"})


class PlanError(ValueError):
    """Invalid plan IR."""


def _req_str(obj: Mapping[str, Any], key: str, ctx: str) -> str:
    val = obj.get(key)
    if not isinstance(val, str) or not val.strip():
        raise PlanError(f"{ctx}: {key} must be a non-empty string")
    return val


def _opt_str(obj: Mapping[str, Any], key: str) -> str | None:
    val = obj.get(key)
    if val is None:
        return None
    if not isinstance(val, str):
        raise PlanError(f"{key} must be a string when present")
    return val


def _int(obj: Mapping[str, Any], key: str, default: int = 0, lo: int = 0) -> int:
    val = obj.get(key, default)
    if val is None:
        val = default
    if isinstance(val, bool) or not isinstance(val, (int, float)):
        raise PlanError(f"{key} must be a number")
    n = int(val)
    if n < lo:
        raise PlanError(f"{key} must be >= {lo}")
    return n


def _float(obj: Mapping[str, Any], key: str, default: float | None = None) -> float | None:
    if key not in obj:
        return default
    val = obj[key]
    if isinstance(val, bool) or not isinstance(val, (int, float)):
        raise PlanError(f"{key} must be a number")
    return float(val)


def validate_recipe(recipe: Mapping[str, Any], ctx: str = "recipe") -> dict[str, Any]:
    if not isinstance(recipe, Mapping):
        raise PlanError(f"{ctx} must be an object")
    name = recipe.get("name", "custom")
    if not isinstance(name, str) or not name:
        raise PlanError(f"{ctx}.name must be a string")
    out: dict[str, Any] = {"name": name}
    for side in ("from", "to"):
        block = recipe.get(side)
        if block is None:
            continue
        if not isinstance(block, Mapping):
            raise PlanError(f"{ctx}.{side} must be an object")
        clean: dict[str, Any] = {}
        for p in RECIPE_PROPS:
            if p not in block:
                continue
            v = block[p]
            if not isinstance(v, (int, float)) or isinstance(v, bool):
                raise PlanError(f"{ctx}.{side}.{p} must be a number")
            clean[p] = float(v)
        out[side] = clean
    out["duration"] = _int(recipe, "duration", 240)
    if out["duration"] > 120_000:
        raise PlanError(f"{ctx}.duration must be <= 120000")
    out["delay"] = _int(recipe, "delay", 0)
    easing = recipe.get("easing", "ease-out")
    if not isinstance(easing, str) or not easing:
        raise PlanError(f"{ctx}.easing must be a string")
    out["easing"] = easing
    fill = recipe.get("fill", "both")
    if fill not in {"none", "forwards", "backwards", "both"}:
        raise PlanError(f"{ctx}.fill must be a fill mode")
    out["fill"] = fill
    if "spring" in recipe:
        spring = recipe["spring"]
        if not isinstance(spring, Mapping):
            raise PlanError(f"{ctx}.spring must be an object")
        out["spring"] = {
            "mass": float(spring.get("mass", 1.0)),
            "stiffness": float(spring.get("stiffness", 280)),
            "damping": float(spring.get("damping", 24)),
        }
        out["engine"] = "spring"
    if "path" in recipe:
        path = recipe["path"]
        if not isinstance(path, Mapping) or not isinstance(path.get("d"), str):
            raise PlanError(f"{ctx}.path.d must be a string")
        out["path"] = {"d": path["d"], "rotate": str(path.get("rotate", "auto"))}
    if "engine" in recipe and recipe["engine"] in ENGINES:
        out["engine"] = recipe["engine"]
    return out


def _validate_node(node: Mapping[str, Any], ctx: str) -> dict[str, Any]:
    if not isinstance(node, Mapping):
        raise PlanError(f"{ctx} must be an object")
    kind = _req_str(node, "kind", ctx)
    if kind == KIND_TRACK:
        return _validate_track(node, ctx)
    if kind == KIND_STAGGER:
        return _validate_stagger(node, ctx)
    if kind == KIND_GROUP:
        return _validate_group(node, ctx)
    if kind == KIND_PHASE:
        return _validate_phase(node, ctx)
    if kind == KIND_SHARE:
        return _validate_share(node, ctx)
    if kind == KIND_BIND:
        return _validate_bind(node, ctx)
    if kind == KIND_SCORE:
        return _validate_score(node, ctx)
    if kind == KIND_CUE:
        return _validate_cue(node, ctx)
    raise PlanError(f"{ctx}: unknown kind {kind!r}")


def _validate_track(node: Mapping[str, Any], ctx: str) -> dict[str, Any]:
    target = _req_str(node, "target", ctx)
    role = node.get("role", "enter")
    if role not in ROLES:
        raise PlanError(f"{ctx}.role must be one of {sorted(ROLES)}")
    after = node.get("after", "keep" if role != "exit" else "remove")
    if after not in AFTERS:
        raise PlanError(f"{ctx}.after must be one of {sorted(AFTERS)}")
    recipe = node.get("recipe")
    if recipe is None:
        raise PlanError(f"{ctx}.recipe is required")
    html = node.get("html")
    if html is not None and not isinstance(html, str):
        if not (
            callable(getattr(html, "__render__", None))
            or callable(getattr(html, "__html__", None))
        ):
            raise PlanError(
                f"{ctx}.html must be a string or a renderable (__render__ / __html__)"
            )
    out: dict[str, Any] = {
        "kind": KIND_TRACK,
        "target": target,
        "role": role,
        "after": after,
        "recipe": validate_recipe(recipe, f"{ctx}.recipe"),
    }
    if html is not None:
        out["html"] = html
    name = _opt_str(node, "name")
    if name:
        out["name"] = name
    return out


def _validate_stagger(node: Mapping[str, Any], ctx: str) -> dict[str, Any]:
    selector = node.get("selector") or node.get("target")
    if not isinstance(selector, str) or not selector.strip():
        raise PlanError(f"{ctx}.selector is required")
    role = node.get("role", "enter")
    if role not in ROLES:
        raise PlanError(f"{ctx}.role must be one of {sorted(ROLES)}")
    recipe = node.get("recipe")
    if recipe is None:
        raise PlanError(f"{ctx}.recipe is required")
    after = node.get("after", "keep")
    if after not in AFTERS:
        after = "keep"
    return {
        "kind": KIND_STAGGER,
        "selector": selector,
        "role": role,
        "gap_ms": _int(node, "gap_ms", 40),
        "recipe": validate_recipe(recipe, f"{ctx}.recipe"),
        "after": after,
    }


def _validate_share(node: Mapping[str, Any], ctx: str) -> dict[str, Any]:
    """Shared presence: named identity the client measures (FLIP)."""
    sid = _req_str(node, "id", ctx)
    leave = _req_str(node, "leave", ctx)
    arrive = _req_str(node, "arrive", ctx)
    recipe = node.get("recipe")
    out: dict[str, Any] = {
        "kind": KIND_SHARE,
        "id": sid,
        "leave": leave,
        "arrive": arrive,
    }
    if recipe is not None:
        out["recipe"] = validate_recipe(recipe, f"{ctx}.recipe")
    else:
        out["recipe"] = validate_recipe(
            {"name": "share", "duration": 320, "easing": "cubic-bezier(0.16, 1, 0.3, 1)", "fill": "both"},
            f"{ctx}.recipe",
        )
    return out


def _validate_bind(node: Mapping[str, Any], ctx: str) -> dict[str, Any]:
    """Bind a plan (or subtree) to scroll/drag/progress — becomes a 0..1 tape."""
    inp = node.get("input", "scroll")
    if inp not in BIND_INPUTS:
        raise PlanError(f"{ctx}.input must be one of {sorted(BIND_INPUTS)}")
    target = _req_str(node, "target", ctx)
    child = node.get("child") or node.get("plan") or node.get("root")
    if child is None:
        raise PlanError(f"{ctx}.child is required")
    out: dict[str, Any] = {
        "kind": KIND_BIND,
        "input": inp,
        "target": target,
        "child": _validate_node(child, f"{ctx}.child"),
    }
    until = _opt_str(node, "until")
    if until:
        out["until"] = until
    axis = _opt_str(node, "axis")
    if axis in {"x", "y", "both"}:
        out["axis"] = axis
    return out


def _validate_score(node: Mapping[str, Any], ctx: str) -> dict[str, Any]:
    """Multi-hop presence: hold exiting nodes until a later cue Result arrives."""
    sid = _req_str(node, "id", ctx)
    child = node.get("child") or node.get("root")
    if child is None:
        raise PlanError(f"{ctx}.child is required")
    out: dict[str, Any] = {
        "kind": KIND_SCORE,
        "id": sid,
        "child": _validate_node(child, f"{ctx}.child"),
    }
    phase = node.get("phase", "now")
    if phase not in {"now", "hold", "resolve"}:
        raise PlanError(f"{ctx}.phase must be now|hold|resolve")
    out["phase"] = phase
    return out


def _validate_cue(node: Mapping[str, Any], ctx: str) -> dict[str, Any]:
    """Cue resolves a score held on the client."""
    score_id = _req_str(node, "score", ctx)
    child = node.get("child")
    out: dict[str, Any] = {"kind": KIND_CUE, "score": score_id}
    if child is not None:
        out["child"] = _validate_node(child, f"{ctx}.child")
    return out


def _validate_group(node: Mapping[str, Any], ctx: str) -> dict[str, Any]:
    mode = node.get("mode", "wait")
    if mode not in MODES:
        raise PlanError(f"{ctx}.mode must be one of {sorted(MODES)}")
    tracks = node.get("tracks") or node.get("children") or []
    if not isinstance(tracks, list):
        raise PlanError(f"{ctx}.tracks must be a list")
    return {
        "kind": KIND_GROUP,
        "name": node.get("name") or "anon",
        "mode": mode,
        "tracks": [_validate_node(t, f"{ctx}.tracks[{i}]") for i, t in enumerate(tracks)],
    }


def _validate_phase(node: Mapping[str, Any], ctx: str) -> dict[str, Any]:
    mode = node.get("mode", "parallel")
    if mode not in MODES:
        raise PlanError(f"{ctx}.mode must be one of {sorted(MODES)}")
    children = node.get("children") or []
    if not isinstance(children, list) or not children:
        raise PlanError(f"{ctx}.children must be a non-empty list")
    return {
        "kind": KIND_PHASE,
        "mode": mode,
        "stagger_ms": _int(node, "stagger_ms", 0),
        "children": [_validate_node(c, f"{ctx}.children[{i}]") for i, c in enumerate(children)],
    }


def validate_plan(plan: Mapping[str, Any]) -> dict[str, Any]:
    """Return a cleaned, canonical plan dict. Raises PlanError."""
    if not isinstance(plan, Mapping):
        raise PlanError("plan must be an object")
    v = plan.get("v", IR_VERSION)
    if str(v) != IR_VERSION:
        raise PlanError(f"unsupported plan version {v!r}")
    kind = plan.get("kind", KIND_PLAN)
    if kind != KIND_PLAN:
        raise PlanError("root kind must be 'plan'")
    interrupt = plan.get("interrupt", "replace")
    if interrupt not in INTERRUPTS:
        raise PlanError(f"interrupt must be one of {sorted(INTERRUPTS)}")
    reduced = plan.get("reduced", "simplify")
    if reduced not in REDUCED:
        raise PlanError(f"reduced must be one of {sorted(REDUCED)}")
    engine = plan.get("engine", "presence")
    if engine not in ENGINES:
        raise PlanError(f"engine must be one of {sorted(ENGINES)}")
    root = plan.get("root")
    if root is None:
        raise PlanError("plan.root is required")
    if "id" not in plan or plan.get("id") is None:
        pid = "plan"
    else:
        pid = plan.get("id")
    if not isinstance(pid, str) or not pid.strip():
        raise PlanError("plan.id must be a non-empty string")
    complete = plan.get("complete")
    if complete is not None and not isinstance(complete, str):
        raise PlanError("plan.complete must be a string action name")
    out: dict[str, Any] = {
        "v": IR_VERSION,
        "kind": KIND_PLAN,
        "id": pid.strip(),
        "interrupt": interrupt,
        "reduced": reduced,
        "engine": engine,
        "root": _validate_node(root, "root"),
    }
    if isinstance(complete, str) and complete.strip():
        out["complete"] = complete.strip()
    alt = plan.get("reduce_tree")
    if alt is not None:
        out["reduce_tree"] = _validate_node(alt, "reduce_tree")
    return out
