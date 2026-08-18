"""Compile raw authoring trees into canonical IR."""

from __future__ import annotations

from typing import Any, Mapping

from ux_motion._ir import validate_plan


def compile_plan(plan: Mapping[str, Any]) -> dict[str, Any]:
    return validate_plan(plan)
