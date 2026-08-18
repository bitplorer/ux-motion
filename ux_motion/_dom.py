"""Scene as a ux-dom tree node.

ux-dom ``_add_unlocked`` only accepts ``dom_tag`` / string / number / dict /
iterable. The face is a Component whose only child is the plan ``<script>``.

HTML trees on the scene are **not** re-parented into this face (that would
steal them from any other tree). ``freeze_plan`` → ``render_markup`` already
runs ``stamp_tree`` on each of them — the same sequence HTMLResponse uses.

Soft-depends on ux-dom. ``motion_tag`` raises if it is not installed.
"""

from __future__ import annotations

from typing import Any


def motion_tag(scene: Any) -> Any:
    try:
        from ux_dom.dom import script
        from ux_dom.dom.src.component import Component
    except ImportError as exc:
        raise ImportError(
            "Scene.tag() requires ux-dom (pip install ux-dom). "
            "Scene.__render__ still works without it."
        ) from exc

    class MotionScript(script):
        """Plan carrier. Body is filled at SERIALIZE, after stamp_tree."""

        def __init__(self, owner: Any) -> None:
            super().__init__(type="application/ux-motion+json", data_ux_motion="plan")
            self._motion_scene = owner

        def _serialized(self) -> str:
            from ux_motion._freeze import freeze_plan
            from ux_motion._wire import encode_plan_script

            return encode_plan_script(freeze_plan(self._motion_scene), pretty=False)

        def _render(self, sb, indent_level=0, indent_str="  ", pretty=True, xhtml=False, _seen=None):
            payload = self._serialized()
            open_bits = ["<script"]
            for tok in self._iter_html_attrs(indent_level, indent_str, pretty):
                open_bits.append(tok)
            open_bits.append(">")
            inner_start = payload.find(">") + 1
            inner = payload[inner_start:] if inner_start > 0 else payload
            sb.append("".join(open_bits) + inner)
            return sb

        def _walk_render_tokens(self, indent_level, indent_str, pretty, xhtml, _seen=None):
            yield from self._render([], indent_level, indent_str, pretty, xhtml, _seen=_seen)

    class MotionScene(Component):
        def __init__(self, owner: Any, *args: Any, **kwargs: Any) -> None:
            self._motion_scene = owner
            super().__init__(*args, **kwargs)

        def render(self, *args: Any, **kwargs: Any):
            return MotionScript(self._motion_scene)

    return MotionScene(scene)
