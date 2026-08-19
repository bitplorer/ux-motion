#!/usr/bin/env python3
"""Minimal runnable sample for ux_motion 1.3.0."""

from __future__ import annotations

from ux_motion import (
    explain,
    fade,
    frames,
    interpret,
    rise,
    scene,
    send,
    share,
    tokens,
)


def main() -> None:
    plan = (
        scene("demo")
        .exit("#old", fade.exit(ms=tokens.ms("exit")), after="hide")
        .enter("#new", rise.enter(ms=tokens.ms("enter")))
        .share("hero", leave="#thumb", arrive="#hero")
        .plan()
    )
    print("=== explain ===")
    print(explain(plan))
    print()
    print("=== events ===")
    for e in interpret(plan):
        print(f"  {e}")
    print()
    print("=== send.play op ===")
    print(send.play(plan)["ops"][0]["op"])
    print()
    print("=== frames svg bytes ===")
    print(len(frames(plan)))


if __name__ == "__main__":
    main()
