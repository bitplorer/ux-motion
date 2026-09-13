#!/usr/bin/env python3
"""Thin Soft 2 sample: morph similar SVG path d. Not offset-path / along."""

from __future__ import annotations

from ux_motion import morph_d, scene, send


def main() -> None:
    rec = morph_d(
        "M0,0 L20,0 L20,20 L0,20 Z",
        "M10,0 L20,10 L10,20 L0,10 Z",
        ms=320,
    )
    plan = scene("icon").enter("#blob", rec).plan()
    print(send.play(plan)["ops"][0]["op"])
    print(plan["root"]["children"][0]["recipe"]["name"])
    print(rec["morph"]["d"]["from"][:6], "→", rec["morph"]["d"]["to"][:6])


if __name__ == "__main__":
    main()
