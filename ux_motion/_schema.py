"""JSON Schema for IR v1 — so other languages can author against the contract."""

from __future__ import annotations

from typing import Any

from ux_motion._contract import CONTRACT


def schema() -> dict[str, Any]:
    """Draft-07 style schema of the plan IR. Additive fields remain valid."""
    return {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "$id": "https://ux-motion.dev/schema/plan-v1.json",
        "title": "ux_motion Plan IR v1",
        "type": "object",
        "required": ["v", "kind", "id", "root"],
        "properties": {
            "v": {"const": "1"},
            "kind": {"const": "plan"},
            "id": {"type": "string", "minLength": 1},
            "interrupt": {"enum": list(CONTRACT["modes"]) and ["replace", "queue", "ignore"]},
            "reduced": {"enum": ["skip", "simplify", "honor", "swap"]},
            "engine": {"enum": list(CONTRACT["engines"])},
            "complete": {"type": "string"},
            "reduce_tree": {"$ref": "#/definitions/node"},
            "root": {"$ref": "#/definitions/node"},
        },
        "definitions": {
            "recipe": {
                "type": "object",
                "required": ["name"],
                "properties": {
                    "name": {"type": "string"},
                    "from": {"type": "object"},
                    "to": {"type": "object"},
                    "duration": {"type": "integer", "minimum": 0, "maximum": 120000},
                    "delay": {"type": "integer", "minimum": 0},
                    "easing": {"type": "string"},
                    "fill": {"enum": ["none", "forwards", "backwards", "both"]},
                    "spring": {
                        "type": "object",
                        "properties": {
                            "mass": {"type": "number"},
                            "stiffness": {"type": "number"},
                            "damping": {"type": "number"},
                        },
                    },
                    "path": {
                        "type": "object",
                        "required": ["d"],
                        "properties": {
                            "d": {"type": "string"},
                            "rotate": {"type": "string"},
                        },
                    },
                    "engine": {"enum": list(CONTRACT["engines"])},
                },
            },
            "node": {
                "type": "object",
                "required": ["kind"],
                "properties": {
                    "kind": {"enum": list(CONTRACT["kinds"])},
                    "target": {"type": "string"},
                    "selector": {"type": "string"},
                    "role": {"enum": list(CONTRACT["roles"])},
                    "after": {"enum": list(CONTRACT["after"])},
                    "recipe": {"$ref": "#/definitions/recipe"},
                    "html": {"type": "string"},
                    "name": {"type": "string"},
                    "mode": {"enum": list(CONTRACT["modes"])},
                    "tracks": {"type": "array", "items": {"$ref": "#/definitions/node"}},
                    "children": {"type": "array", "items": {"$ref": "#/definitions/node"}},
                    "stagger_ms": {"type": "integer", "minimum": 0},
                    "gap_ms": {"type": "integer", "minimum": 0},
                    "id": {"type": "string"},
                    "leave": {"type": "string"},
                    "arrive": {"type": "string"},
                    "input": {"enum": list(CONTRACT["bind_inputs"])},
                    "child": {"$ref": "#/definitions/node"},
                    "until": {"type": "string"},
                    "axis": {"enum": ["x", "y", "both"]},
                    "phase": {"enum": ["now", "hold", "resolve"]},
                    "score": {"type": "string"},
                },
            },
        },
    }
