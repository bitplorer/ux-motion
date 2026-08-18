"""How a plan leaves the server.

    send.play(plan)     →  animate it
    send.update(plan)   →  just change the DOM
    send.rewind(plan)   →  play the inverted scene
    send.cancel(id)     →  stop in-flight motion
"""

from __future__ import annotations

from typing import Any, Mapping

from ux_motion._compile import compile_plan
from ux_motion._ops import as_update, cancel as emit_cancel, play, rewind, to_result


class Send:
    """The thing you call when a scene is ready to leave the server."""

    def play(
        self,
        plan: Mapping[str, Any],
        *,
        also_update: bool = False,
        action: str | None = None,
    ) -> dict[str, Any]:
        frozen = compile_plan(plan)
        ops = play(frozen)
        if also_update:
            ops[0].setdefault("meta", {})
            ops[0]["meta"]["update"] = as_update(frozen)
        return to_result(ops, action=action)

    def update(self, plan: Mapping[str, Any], *, action: str | None = None) -> dict[str, Any]:
        return to_result(as_update(compile_plan(plan)), action=action)

    def rewind(self, plan: Mapping[str, Any], *, action: str | None = None) -> dict[str, Any]:
        return to_result(rewind(compile_plan(plan)), action=action)

    def cancel(self, plan_id: str | None = None, *, action: str | None = None) -> dict[str, Any]:
        return to_result(emit_cancel(plan_id), action=action)


send = Send()
