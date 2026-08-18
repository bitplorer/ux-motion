"""Named recipes. A name must look like what it does."""

from __future__ import annotations

from typing import Any

from ux_motion._tokens import tokens


class Recipe(dict):
    """A serializable animation recipe (from/to + timing + optional physics/path)."""

    def with_delay(self, ms: int) -> "Recipe":
        out = Recipe(self)
        out["delay"] = int(ms)
        return out

    def with_duration(self, ms: int) -> "Recipe":
        out = Recipe(self)
        out["duration"] = int(ms)
        return out

    def with_easing(self, easing: str) -> "Recipe":
        out = Recipe(self)
        out["easing"] = easing
        return out

    def with_spring(self, name: str = "snappy", **params: float) -> "Recipe":
        out = Recipe(self)
        body = tokens.spring_params(name)
        body.update({k: float(v) for k, v in params.items()})
        out["spring"] = body
        out["engine"] = "spring"
        return out

    def with_path(self, d: str, *, rotate: str = "auto") -> "Recipe":
        out = Recipe(self)
        out["path"] = {"d": d, "rotate": rotate}
        return out


def _recipe(
    name: str,
    *,
    frm: dict[str, float] | None = None,
    to: dict[str, float] | None = None,
    duration: int = 240,
    delay: int = 0,
    easing: str = "ease-out",
    fill: str = "both",
    **extra: Any,
) -> Recipe:
    body: dict[str, Any] = {
        "name": name,
        "duration": int(duration),
        "delay": int(delay),
        "easing": easing,
        "fill": fill,
    }
    if frm:
        body["from"] = {k: float(v) for k, v in frm.items()}
    if to:
        body["to"] = {k: float(v) for k, v in to.items()}
    body.update(extra)
    return Recipe(body)


class _Family:
    """Parametric enter/exit pair. Defaults make the name true."""

    def __init__(
        self,
        name: str,
        *,
        enter: dict[str, float] | None = None,
        exit: dict[str, float] | None = None,
    ) -> None:
        self.name = name
        self._enter = dict(enter or {})
        self._exit = dict(exit or {})

    def enter(
        self,
        *,
        y: float | None = None,
        x: float | None = None,
        scale: float | None = None,
        opacity: float | None = None,
        blur: float | None = None,
        ms: int | None = None,
        delay: int = 0,
        easing: str | None = None,
        rotate: float = 0,
    ) -> Recipe:
        d = dict(self._enter)
        if y is not None:
            d["y"] = y
        if x is not None:
            d["x"] = x
        if scale is not None:
            d["scale"] = scale
        if opacity is not None:
            d["opacity"] = opacity
        if blur is not None:
            d["blur"] = blur
        frm: dict[str, float] = {
            "opacity": float(d.get("opacity", 0)),
            "x": float(d.get("x", 0)),
            "y": float(d.get("y", 0)),
        }
        if "scale" in d:
            frm["scale"] = float(d["scale"])
        if rotate:
            frm["rotate"] = rotate
        if d.get("blur"):
            frm["blur"] = float(d["blur"])
        to: dict[str, float] = {"opacity": 1, "x": 0, "y": 0, "scale": 1, "rotate": 0, "blur": 0}
        return _recipe(
            f"{self.name}.enter",
            frm=frm,
            to=to,
            duration=ms if ms is not None else tokens.ms("enter"),
            delay=delay,
            easing=easing or tokens.ease("enter"),
        )

    def exit(
        self,
        *,
        y: float | None = None,
        x: float | None = None,
        scale: float | None = None,
        opacity: float | None = None,
        blur: float | None = None,
        ms: int | None = None,
        delay: int = 0,
        easing: str | None = None,
        rotate: float = 0,
    ) -> Recipe:
        d = dict(self._exit)
        if y is not None:
            d["y"] = y
        if x is not None:
            d["x"] = x
        if scale is not None:
            d["scale"] = scale
        if opacity is not None:
            d["opacity"] = opacity
        if blur is not None:
            d["blur"] = blur
        to: dict[str, float] = {
            "opacity": float(d.get("opacity", 0)),
            "x": float(d.get("x", 0)),
            "y": float(d.get("y", 0)),
        }
        if "scale" in d:
            to["scale"] = float(d["scale"])
        if rotate:
            to["rotate"] = rotate
        if d.get("blur"):
            to["blur"] = float(d["blur"])
        frm: dict[str, float] = {"opacity": 1, "x": 0, "y": 0, "scale": 1, "rotate": 0, "blur": 0}
        return _recipe(
            f"{self.name}.exit",
            frm=frm,
            to=to,
            duration=ms if ms is not None else tokens.ms("exit"),
            delay=delay,
            easing=easing or tokens.ease("exit"),
        )

    def __call__(self, node=None, /, **kwargs):
        """Drop-in HOF: ``rise(tree)`` → Scene. ``rise()`` / ``rise(ms=180)`` → Recipe."""
        from ux_motion._hof import apply_family

        return apply_family(self, node, **kwargs)


fade = _Family("fade")
slide = _Family("slide", enter={"x": tokens.dist("md")}, exit={"x": -tokens.dist("md")})
scale = _Family("scale", enter={"scale": 0.94, "opacity": 0}, exit={"scale": 0.96, "opacity": 0})
rise = _Family("rise", enter={"y": tokens.dist("sm")}, exit={"y": -tokens.dist("xs")})
blur = _Family("blur", enter={"blur": 8, "opacity": 0}, exit={"blur": 8, "opacity": 0})


def none(*, ms: int = 0) -> Recipe:
    return _recipe("none", frm={"opacity": 1}, to={"opacity": 1}, duration=ms, easing="linear")


def snap() -> Recipe:
    return none(ms=0)


def along(
    path_d: str,
    *,
    ms: int | None = None,
    delay: int = 0,
    easing: str | None = None,
    rotate: str = "auto",
    opacity_from: float = 0,
) -> Recipe:
    """Move along an SVG path (offset-path). The river.ai origin story."""
    rec = _recipe(
        "along",
        frm={"opacity": opacity_from, "offset": 0},
        to={"opacity": 1, "offset": 1},
        duration=ms if ms is not None else tokens.ms("page"),
        delay=delay,
        easing=easing or tokens.ease("soft"),
    )
    return rec.with_path(path_d, rotate=rotate)


def springy(
    *,
    y: float | None = None,
    x: float | None = None,
    scale: float | None = None,
    preset: str = "snappy",
    ms: int | None = None,
) -> Recipe:
    """Enter with spring physics."""
    rec = rise.enter(y=y if y is not None else tokens.dist("sm"), x=x or 0, scale=scale, ms=ms)
    return rec.with_spring(preset)
