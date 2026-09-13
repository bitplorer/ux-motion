"""Soft 1 — scroll-scrub lock.

IR bind KEEP. Player exports UxMotion.scrub. Python scrub seeks the tape.
No gesture APIs. drag/progress leftover is not this Soft.
"""
from __future__ import annotations

import unittest

from ux_motion import (
    CONTRACT,
    ScrubFrame,
    bind,
    fade,
    interpret,
    rise,
    scene,
    scrub,
    span_ms,
    track,
    validate_plan,
)


class TestSoft1ScrubTape(unittest.TestCase):
    def test_bind_ir_fields_unchanged(self) -> None:
        plan = scene("essay").bind_to("scroll", "#article").enter("#fig", rise.enter(ms=80)).plan()
        root = plan["root"]
        self.assertEqual(root["kind"], "bind")
        self.assertEqual(root["input"], "scroll")
        self.assertEqual(root["target"], "#article")
        self.assertIn("child", root)
        self.assertNotIn("whileHover", root)
        self.assertEqual(set(root) - {"until", "axis"}, {"kind", "input", "target", "child"})

    def test_bind_inputs_keep_scroll_drag_progress(self) -> None:
        self.assertEqual(CONTRACT["bind_inputs"], ("scroll", "drag", "progress"))

    def test_scrub_seeks_logical_tape(self) -> None:
        plan = scene("essay").bind_to("scroll", "#article").enter("#fig", rise.enter(ms=80)).plan()
        start = scrub(plan, 0)
        mid = scrub(plan, 0.5)
        end = scrub(plan, 1)
        self.assertIsInstance(mid, ScrubFrame)
        self.assertEqual(start.progress, 0.0)
        self.assertEqual(start.t, 0)
        self.assertEqual(end.progress, 1.0)
        self.assertEqual(end.t, span_ms(plan))
        self.assertEqual(end.t, mid.span)
        self.assertEqual(mid.t, int(round(0.5 * mid.span)))
        self.assertTrue(any(e.target == "#fig" and e.event == "start" for e in start.started))
        self.assertTrue(any(e.target == "#fig" for e in mid.active) or mid.span == 0)
        self.assertTrue(any(e.target == "#fig" and e.event == "end" for e in end.ended))
        self.assertEqual(end.active, ())

    def test_scrub_clamps_progress(self) -> None:
        plan = scene("essay").bind_to("scroll", "#article").enter("#fig", fade.enter(ms=40)).plan()
        lo = scrub(plan, -2)
        hi = scrub(plan, 4)
        self.assertEqual(lo.progress, 0.0)
        self.assertEqual(lo.t, 0)
        self.assertEqual(hi.progress, 1.0)
        self.assertEqual(hi.t, span_ms(plan))

    def test_scrub_matches_interpret_events(self) -> None:
        plan = (
            scene("nav")
            .bind_to("scroll", "#page")
            .exit("#old", fade.exit(ms=50))
            .enter("#new", fade.enter(ms=50))
            .plan()
        )
        ev = interpret(plan)
        frame = scrub(plan, 1)
        self.assertEqual(frame.span, max(e.t for e in ev))
        self.assertEqual({(e.target, e.role) for e in ev if e.event == "end"}, {(e.target, e.role) for e in frame.ended})

    def test_functional_bind_still_validates(self) -> None:
        child = track("#fig", rise.enter(ms=40))
        node = bind("scroll", "#article", child)
        plan = scene("fn").also(node).plan()
        validate_plan(plan)
        self.assertEqual(scrub(plan, 0).progress, 0.0)

    def test_contract_freezes_scrub_export_name(self) -> None:
        self.assertEqual(CONTRACT["scrub"], "UxMotion.scrub")
        self.assertIn("scrub", CONTRACT["player_exports"])
        self.assertEqual(
            CONTRACT["player_exports"],
            ("play", "applyOp", "applyOps", "cancel", "boot", "scrub", "version"),
        )


class TestSoft1PlayerSource(unittest.TestCase):
    def _player(self) -> str:
        from pathlib import Path

        return (Path(__file__).resolve().parents[1] / "static" / "ux-motion-player.js").read_text(
            encoding="utf-8"
        )

    def test_player_exports_scrub(self) -> None:
        js = self._player()
        self.assertIn("scrub: scrub,", js)
        self.assertIn("function scrub(planId, progress)", js)
        self.assertIn("function attachScrollLoop(", js)
        self.assertIn("function applyTape(", js)
        self.assertIn("function measureScrollProgress(", js)
        self.assertIn("function collectTape(", js)
        self.assertIn("anim.currentTime", js)
        self.assertIn("requestAnimationFrame", js)
        self.assertIn('data-uxm-progress"', js)
        self.assertIn("tapes.set(planId, tape)", js)

    def test_scroll_bind_does_not_oneshot_child(self) -> None:
        js = self._player()
        bind_fn = js.split("function playBind(")[1].split("function playScore(")[0]
        self.assertIn('node.input === "scroll"', bind_fn)
        self.assertIn("attachScrollLoop(tape)", bind_fn)
        self.assertNotIn("Hosts that want continuous scrub call UxMotion.scrub", bind_fn)

    def test_viewport_progress_formula_kept(self) -> None:
        js = self._player()
        self.assertIn("(rect.top + h) / (vh + h)", js)


if __name__ == "__main__":
    unittest.main()
