"""Soft 3 — wait completeness lock.

Exit-before-enter for direct tracks. Nested units stay independent.
Soft 1 scrub KEEP. Soft 2 morph_d KEEP. No gesture APIs.
"""
from __future__ import annotations

import unittest

from ux_motion import (
    CONTRACT,
    WAIT_BAGS,
    WAIT_CLOCKS,
    WaitBags,
    WaitClock,
    fade,
    group,
    interpret,
    morph_d,
    partition_wait,
    rise,
    scene,
    scrub,
    sequence,
    share,
    span_ms,
    stagger,
    track,
    validate_plan,
    wait,
    wait_clocks,
)


class TestSoft3WaitBagsAndClocks(unittest.TestCase):
    def test_contract_freezes_wait_completeness_names(self) -> None:
        self.assertEqual(CONTRACT["wait.bags"], ("exits", "stays", "enters", "nested"))
        self.assertEqual(CONTRACT["wait.clocks"], ("exit_end", "stay_end", "enter_t"))
        self.assertEqual(CONTRACT["partition_wait"], "partitionWait")
        self.assertEqual(WAIT_BAGS, CONTRACT["wait.bags"])
        self.assertEqual(WAIT_CLOCKS, CONTRACT["wait.clocks"])
        self.assertEqual(
            CONTRACT["player_exports"],
            ("play", "applyOp", "applyOps", "cancel", "boot", "scrub", "version"),
        )

    def test_classic_exit_before_enter(self) -> None:
        plan = scene("nav").exit("#old", fade.exit(ms=100)).enter("#new", fade.enter(ms=80)).plan()
        clock = wait_clocks(plan)
        self.assertIsInstance(clock, WaitClock)
        self.assertIsInstance(clock.bags, WaitBags)
        self.assertEqual([c["target"] for c in clock.bags.exits], ["#old"])
        self.assertEqual([c["target"] for c in clock.bags.enters], ["#new"])
        self.assertEqual(clock.bags.stays, ())
        self.assertEqual(clock.bags.nested, ())
        self.assertEqual(clock.t0, 0)
        self.assertEqual(clock.exit_end, 100)
        self.assertEqual(clock.stay_end, 100)
        self.assertEqual(clock.enter_t, 100)
        self.assertEqual(clock.end, 180)
        ev = interpret(plan)
        new_start = next(e.t for e in ev if e.target == "#new" and e.event == "start")
        old_end = next(e.t for e in ev if e.target == "#old" and e.event == "end")
        self.assertEqual(new_start, clock.enter_t)
        self.assertGreaterEqual(new_start, old_end)

    def test_missing_role_is_enter(self) -> None:
        bags = partition_wait(
            (
                {"kind": "track", "target": "#x", "recipe": fade.enter(ms=10)},
                {"kind": "track", "target": "#y", "role": "exit", "recipe": fade.exit(ms=10)},
            )
        )
        self.assertEqual([c["target"] for c in bags.enters], ["#x"])
        self.assertEqual([c["target"] for c in bags.exits], ["#y"])
        self.assertEqual(bags.stays, ())

    def test_layout_joins_stays_bag(self) -> None:
        bags = partition_wait(
            (
                track("#a", fade.exit(ms=40), role="exit"),
                track("#b", fade.enter(ms=20), role="layout"),
                track("#c", fade.enter(ms=20), role="stay"),
                track("#d", fade.enter(ms=10)),
            )
        )
        self.assertEqual([c["target"] for c in bags.stays], ["#b", "#c"])
        self.assertEqual([c["target"] for c in bags.enters], ["#d"])

    def test_stays_after_exits_before_enters(self) -> None:
        plan = (
            scene("dock")
            .exit("#old", fade.exit(ms=50))
            .stay("#rail", fade.enter(ms=40))
            .enter("#new", fade.enter(ms=30))
            .plan()
        )
        clock = wait_clocks(plan)
        self.assertEqual(clock.exit_end, 50)
        self.assertEqual(clock.stay_end, 90)
        self.assertEqual(clock.enter_t, 90)
        self.assertEqual(clock.end, 120)
        ev = interpret(plan)
        rail_start = next(e.t for e in ev if e.target == "#rail" and e.event == "start")
        new_start = next(e.t for e in ev if e.target == "#new" and e.event == "start")
        self.assertEqual(rail_start, clock.exit_end)
        self.assertEqual(new_start, clock.enter_t)

    def test_no_exits_no_stays_enters_at_t0(self) -> None:
        plan = scene("in").enter("#new", fade.enter(ms=60)).plan()
        clock = wait_clocks(plan)
        self.assertEqual(clock.exit_end, 0)
        self.assertEqual(clock.stay_end, 0)
        self.assertEqual(clock.enter_t, 0)
        self.assertEqual(clock.end, 60)

    def test_stays_without_exits_start_at_t0(self) -> None:
        plan = scene("hold").stay("#rail", fade.enter(ms=40)).enter("#new", fade.enter(ms=20)).plan()
        clock = wait_clocks(plan)
        self.assertEqual(clock.exit_end, 0)
        self.assertEqual(clock.stay_end, 40)
        self.assertEqual(clock.enter_t, 40)

    def test_nested_group_is_independent_unit(self) -> None:
        inner = group(
            "stage",
            track("#a", fade.exit(ms=80), role="exit"),
            track("#b", fade.enter(ms=40)),
            mode="wait",
        )
        plan = scene("outer").also(
            inner,
            track("#c", fade.exit(ms=100), role="exit"),
            track("#d", fade.enter(ms=20)),
        ).plan()
        clock = wait_clocks(plan)
        self.assertEqual(len(clock.bags.nested), 1)
        self.assertEqual(clock.bags.nested[0]["kind"], "group")
        self.assertEqual([c["target"] for c in clock.bags.exits], ["#c"])
        self.assertEqual([c["target"] for c in clock.bags.enters], ["#d"])
        self.assertEqual(clock.exit_end, 100)
        self.assertEqual(clock.enter_t, 100)
        ev = interpret(plan)
        a_start = next(e.t for e in ev if e.target == "#a" and e.event == "start")
        b_start = next(e.t for e in ev if e.target == "#b" and e.event == "start")
        d_start = next(e.t for e in ev if e.target == "#d" and e.event == "start")
        self.assertEqual(a_start, 0)
        self.assertEqual(b_start, 80)
        self.assertEqual(d_start, 100)

    def test_share_and_sequence_are_nested_not_flattened(self) -> None:
        bags = partition_wait(
            (
                track("#old", fade.exit(ms=50), role="exit"),
                share("hero", leave="#g", arrive="#p"),
                sequence(track("#rail-a", fade.exit(ms=10), role="exit")),
                track("#new", fade.enter(ms=20)),
            )
        )
        self.assertEqual(len(bags.nested), 2)
        self.assertEqual(bags.nested[0]["kind"], "share")
        self.assertEqual(bags.nested[1]["kind"], "phase")
        self.assertEqual(bags.nested[1]["mode"], "sequence")

    def test_stagger_exit_delays_enter(self) -> None:
        plan = scene("list").also(
            stagger(".gone", fade.exit(ms=50), role="exit", gap_ms=10),
            track("#new", fade.enter(ms=20)),
        ).plan()
        clock = wait_clocks(plan)
        self.assertEqual(len(clock.bags.exits), 1)
        self.assertEqual(clock.bags.exits[0]["kind"], "stagger")
        self.assertEqual(clock.exit_end, 70)
        self.assertEqual(clock.enter_t, 70)

    def test_phase_stagger_ms_does_not_apply_to_wait(self) -> None:
        node = wait(
            track("#old", fade.exit(ms=40), role="exit"),
            track("#new", fade.enter(ms=20)),
        )
        node["stagger_ms"] = 999
        plan = validate_plan({"v": "1", "kind": "plan", "id": "gap", "root": node})
        clock = wait_clocks(plan)
        self.assertEqual(clock.enter_t, 40)
        self.assertEqual(clock.exit_end, 40)

    def test_wait_clocks_unwraps_bind_child(self) -> None:
        plan = (
            scene("essay")
            .bind_to("scroll", "#article")
            .exit("#old", fade.exit(ms=50))
            .enter("#new", fade.enter(ms=50))
            .plan()
        )
        clock = wait_clocks(plan)
        self.assertEqual(clock.enter_t, 50)
        self.assertEqual(clock.exit_end, 50)

    def test_functional_wait_node_mode(self) -> None:
        node = wait(track("#old", fade.exit(ms=10), role="exit"), track("#new", rise.enter(ms=10)))
        self.assertEqual(node["mode"], "wait")
        self.assertEqual(node["kind"], "phase")


class TestSoft1Soft2Regression(unittest.TestCase):
    def test_scrub_still_seeks(self) -> None:
        plan = scene("essay").bind_to("scroll", "#article").enter("#fig", rise.enter(ms=80)).plan()
        mid = scrub(plan, 0.5)
        self.assertEqual(mid.progress, 0.5)
        self.assertEqual(mid.t, int(round(0.5 * mid.span)))
        self.assertEqual(mid.span, span_ms(plan))
        self.assertEqual(CONTRACT["scrub"], "UxMotion.scrub")

    def test_morph_d_still_additive(self) -> None:
        rec = morph_d("M0,0 L10,0", "M0,10 L10,10", ms=80)
        self.assertEqual(rec["name"], "morph.d")
        self.assertEqual(CONTRACT["morph.d"], "morph.d")
        self.assertNotIn("path", rec)
        plan = scene("icon").enter("#blob", rec).plan()
        self.assertEqual(plan["root"]["children"][0]["recipe"]["morph"]["d"]["from"], "M0,0 L10,0")


class TestSoft3PlayerSource(unittest.TestCase):
    def _player(self) -> str:
        from pathlib import Path

        return (Path(__file__).resolve().parents[1] / "static" / "ux-motion-player.js").read_text(
            encoding="utf-8"
        )

    def test_player_extracts_partition_wait(self) -> None:
        js = self._player()
        self.assertIn("function partitionWait(", js)
        self.assertIn("bags.exits", js)
        self.assertIn("bags.stays", js)
        self.assertIn("bags.enters", js)
        self.assertIn("bags.nested", js)
        self.assertIn('var role = n.role || "enter"', js)
        self.assertIn("waitBags.exits", js)
        self.assertIn("waitBags.nested", js)

    def test_scrub_and_morph_kept(self) -> None:
        js = self._player()
        self.assertIn("function scrub(planId, progress)", js)
        self.assertIn("function morphD(", js)
        self.assertIn("function attachScrollLoop(", js)
        self.assertNotIn("whileHover", js)
        self.assertNotIn("whileTap", js)


if __name__ == "__main__":
    unittest.main()
