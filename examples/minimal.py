#!/usr/bin/env python3
"""Minimal runnable sample for ux_motion 1.0.0."""
from __future__ import annotations
from ux_motion import explain, fade, frames, interpret, rise, scene, send, tokens

def main() -> None:
    plan = (
        scene("demo")
        .exit("#old", fade.exit(ms=tokens.ms("exit")), after="hide")
        .enter("#new", rise.enter(ms=tokens.ms("enter")))
        .plan()
    )
    print(explain(plan))
    print(send.play(plan)["ops"][0]["op"])
    print(len(frames(plan)))

if __name__ == "__main__":
    main()
