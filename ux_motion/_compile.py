"""Compile raw authoring trees into canonical IR.

``compile_plan`` is BUILD: trees on ``html`` stay trees.
``freeze_plan`` is SERIALIZE: official ``__render__``, then string IR.
"""

from __future__ import annotations

from typing import Any, Mapping

from ux_motion._freeze import freeze_plan
from ux_motion._ir import validate_plan


def compile_plan(plan: Mapping[str, Any], *, freeze: bool = False) -> dict[str, Any]:
    if freeze:
        return freeze_plan(plan)
    return validate_plan(plan)
