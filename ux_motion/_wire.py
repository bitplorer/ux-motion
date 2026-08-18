"""JSON is the shared language for a plan."""

from __future__ import annotations

import json
from typing import Any

from ux_motion._ir import PlanError, validate_plan


def dumps(plan: Any, *, indent: int | None = 2) -> str:
    frozen = validate_plan(plan) if isinstance(plan, dict) and plan.get("kind") == "plan" else plan
    return json.dumps(frozen, indent=indent, sort_keys=True, ensure_ascii=False)


def loads(text: str) -> dict[str, Any]:
    try:
        data = json.loads(text)
    except json.JSONDecodeError as e:
        raise PlanError(f"invalid json: {e}") from e
    if not isinstance(data, dict):
        raise PlanError("plan json must be an object")
    return validate_plan(data)
