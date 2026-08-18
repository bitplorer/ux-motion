"""JSON is the shared language for a plan on the wire.

``dumps`` is serialize: freeze html trees through official ``__render__``,
then emit JSON. ``loads`` validates the string-only IR.
"""

from __future__ import annotations

import json
from typing import Any, Mapping

from ux_motion._freeze import freeze_plan
from ux_motion._ir import PlanError, validate_plan


def encode_plan_script(plan: Mapping[str, Any], *, pretty: bool = False) -> str:
    """HTML form of a frozen plan — the string HTMLResponse / a tree walk emit.

    A ``<script type="application/ux-motion+json">`` carries **all**
    information (identity, recipes, serialized markup). ``<`` is escaped
    so markup inside JSON cannot break out of the script element.
    """
    payload = json.dumps(
        plan,
        indent=2 if pretty else None,
        sort_keys=True,
        ensure_ascii=False,
        separators=None if pretty else (",", ":"),
    ).replace("<", "\\u003c")
    return f'<script type="application/ux-motion+json" data-ux-motion="plan">{payload}</script>'


def dumps(plan: Any, *, indent: int | None = 2) -> str:
    frozen = freeze_plan(plan)
    return json.dumps(frozen, indent=indent, sort_keys=True, ensure_ascii=False)


def loads(text: str) -> dict[str, Any]:
    try:
        data = json.loads(text)
    except json.JSONDecodeError as e:
        raise PlanError(f"invalid json: {e}") from e
    if not isinstance(data, dict):
        raise PlanError("plan json must be an object")
    return validate_plan(data)
