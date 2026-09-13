#!/usr/bin/env python3
"""Thin Soft 3 sample: wait clocks. Exits finish before enters."""

from __future__ import annotations

from ux_motion import fade, scene, wait_clocks


def main() -> None:
    plan = scene("nav").exit("#old", fade.exit(ms=100)).enter("#new", fade.enter(ms=80)).plan()
    clock = wait_clocks(plan)
    print(plan["root"]["mode"])
    print("exit_end", clock.exit_end, "enter_t", clock.enter_t)


if __name__ == "__main__":
    main()
