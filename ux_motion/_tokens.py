"""Motion tokens — named timing and distance. Prefer tokens over raw numbers."""

from __future__ import annotations

from typing import Any


class Tokens:
    """Stable design-system values. Override via Tokens.override in hosts if needed."""

    duration = {
        "instant": 0,
        "fast": 120,
        "enter": 280,
        "exit": 220,
        "page": 360,
        "modal": 320,
        "stagger": 40,
        "spring": 480,
    }

    easing = {
        "linear": "linear",
        "enter": "cubic-bezier(0.16, 1, 0.3, 1)",
        "exit": "cubic-bezier(0.4, 0, 1, 1)",
        "soft": "cubic-bezier(0.33, 1, 0.68, 1)",
        "snap": "cubic-bezier(0.2, 0.8, 0.2, 1)",
    }

    distance = {
        "xs": 8,
        "sm": 16,
        "md": 24,
        "lg": 40,
        "xl": 64,
    }

    spring = {
        "snappy": {"mass": 1.0, "stiffness": 280, "damping": 24},
        "gentle": {"mass": 1.2, "stiffness": 120, "damping": 18},
        "wobbly": {"mass": 1.0, "stiffness": 180, "damping": 12},
        "stiff": {"mass": 1.0, "stiffness": 400, "damping": 30},
    }

    @classmethod
    def ms(cls, name: str, default: int = 280) -> int:
        return int(cls.duration.get(name, default))

    @classmethod
    def ease(cls, name: str, default: str = "ease-out") -> str:
        return str(cls.easing.get(name, default))

    @classmethod
    def dist(cls, name: str, default: float = 16) -> float:
        return float(cls.distance.get(name, default))

    @classmethod
    def spring_params(cls, name: str = "snappy") -> dict[str, float]:
        return dict(cls.spring.get(name, cls.spring["snappy"]))

    @classmethod
    def as_dict(cls) -> dict[str, Any]:
        return {
            "duration": dict(cls.duration),
            "easing": dict(cls.easing),
            "distance": dict(cls.distance),
            "spring": {k: dict(v) for k, v in cls.spring.items()},
        }


tokens = Tokens()
