#!/usr/bin/env python3
"""Thin Soft 1 sample: scroll bind is a 0..1 tape, not a gesture."""

from __future__ import annotations

from ux_motion import rise, scrub, send, scene


def main() -> None:
    plan = (
        scene("essay")
        .bind_to("scroll", "#article")
        .enter("#fig", rise.enter(ms=400))
        .plan()
    )
    mid = scrub(plan, 0.5)
    print(send.play(plan)["ops"][0]["op"])
    print(f"progress={mid.progress} t={mid.t} span={mid.span}")
    print("active", [e.target for e in mid.active])


if __name__ == "__main__":
    main()
