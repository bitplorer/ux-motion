"""Soft 2 — SVG path d morph lock.

along / path stays offset-path. morph.d is additive interpolation of similar
SVG path d strings. Soft 1 scrub KEEP. No gesture APIs.
"""
from __future__ import annotations

import unittest

from ux_motion import (
    CONTRACT,
    PlanError,
    along,
    fade,
    morph_d,
    rewind_plan,
    rise,
    scene,
    schema,
    scrub,
    span_ms,
    validate_plan,
)


SQUARE = "M0,0 L20,0 L20,20 L0,20 Z"
DIAMOND = "M10,0 L20,10 L10,20 L0,10 Z"


class TestSoft2MorphDRecipe(unittest.TestCase):
    def test_morph_d_frozen_name_and_ir(self) -> None:
        rec = morph_d(SQUARE, DIAMOND, ms=240)
        self.assertEqual(rec["name"], "morph.d")
        self.assertEqual(rec["morph"]["d"]["from"], SQUARE)
        self.assertEqual(rec["morph"]["d"]["to"], DIAMOND)
        self.assertNotIn("path", rec)
        self.assertEqual(rec["duration"], 240)

    def test_along_is_still_offset_path_not_morph(self) -> None:
        rec = along("M0,0 C50,100 150,100 200,0", ms=400)
        self.assertIn("path", rec)
        self.assertEqual(rec["path"]["d"][:2], "M0")
        self.assertNotIn("morph", rec)
        self.assertEqual(rec["name"], "along")

    def test_with_morph_d_is_additive(self) -> None:
        rec = fade.enter(ms=80).with_morph_d(SQUARE, DIAMOND)
        self.assertEqual(rec["name"], "fade.enter")
        self.assertEqual(rec["morph"]["d"]["from"], SQUARE)
        self.assertEqual(rec["morph"]["d"]["to"], DIAMOND)

    def test_plan_validates_and_keeps_morph_d(self) -> None:
        plan = scene("icon").enter("#blob", morph_d(SQUARE, DIAMOND, ms=80)).plan()
        frozen = validate_plan(plan)
        recipe = frozen["root"]["children"][0]["recipe"]
        self.assertEqual(recipe["name"], "morph.d")
        self.assertEqual(recipe["morph"]["d"]["from"], SQUARE)
        self.assertEqual(recipe["morph"]["d"]["to"], DIAMOND)
        again = validate_plan(frozen)
        self.assertEqual(again["root"]["children"][0]["recipe"]["morph"], recipe["morph"])

    def test_unknown_morph_fields_are_ignored(self) -> None:
        plan = scene("x").enter(
            "#p",
            {
                "name": "morph.d",
                "duration": 40,
                "morph": {
                    "d": {"from": SQUARE, "to": DIAMOND, "extra": "nope"},
                    "mystery": True,
                },
                "invented": 1,
            },
        ).plan()
        recipe = validate_plan(plan)["root"]["children"][0]["recipe"]
        self.assertEqual(recipe["morph"], {"d": {"from": SQUARE, "to": DIAMOND}})
        self.assertNotIn("invented", recipe)
        self.assertNotIn("mystery", recipe["morph"])
        self.assertNotIn("extra", recipe["morph"]["d"])

    def test_path_key_is_not_reused_for_morph(self) -> None:
        plan = scene("x").enter(
            "#p",
            {
                "name": "along",
                "duration": 40,
                "from": {"offset": 0},
                "to": {"offset": 1},
                "path": {"d": SQUARE, "rotate": "auto"},
            },
        ).plan()
        recipe = validate_plan(plan)["root"]["children"][0]["recipe"]
        self.assertEqual(recipe["path"]["d"], SQUARE)
        self.assertNotIn("morph", recipe)

    def test_incomplete_morph_d_raises(self) -> None:
        with self.assertRaises(PlanError):
            validate_plan(
                scene("x")
                .enter("#p", {"name": "morph.d", "duration": 40, "morph": {"d": {"from": SQUARE}}})
                .plan()
            )
        with self.assertRaises(PlanError):
            validate_plan(
                scene("x")
                .enter("#p", {"name": "morph.d", "duration": 40, "morph": {"d": {"to": DIAMOND}}})
                .plan()
            )
        with self.assertRaises(PlanError):
            validate_plan(
                scene("x")
                .enter("#p", {"name": "morph.d", "duration": 40, "morph": {"d": "M0,0 L1,1"}})
                .plan()
            )

    def test_rewind_swaps_morph_d_from_to(self) -> None:
        plan = scene("icon").enter("#blob", morph_d(SQUARE, DIAMOND, ms=80)).plan()
        inv = rewind_plan(plan)
        recipe = inv["root"]["children"][0]["recipe"]
        self.assertEqual(recipe["morph"]["d"]["from"], DIAMOND)
        self.assertEqual(recipe["morph"]["d"]["to"], SQUARE)

    def test_schema_lists_morph_d(self) -> None:
        rec = schema()["definitions"]["recipe"]["properties"]
        self.assertIn("morph", rec)
        self.assertIn("d", rec["morph"]["properties"])
        self.assertIn("path", rec)

    def test_contract_freezes_morph_d_name(self) -> None:
        self.assertEqual(CONTRACT["morph.d"], "morph.d")
        self.assertEqual(
            CONTRACT["player_exports"],
            ("play", "applyOp", "applyOps", "cancel", "boot", "scrub", "version"),
        )


class TestSoft1ScrubRegression(unittest.TestCase):
    def test_scroll_bind_scrub_still_seeks(self) -> None:
        plan = scene("essay").bind_to("scroll", "#article").enter("#fig", rise.enter(ms=80)).plan()
        mid = scrub(plan, 0.5)
        self.assertEqual(mid.progress, 0.5)
        self.assertEqual(mid.t, int(round(0.5 * mid.span)))
        self.assertEqual(mid.span, span_ms(plan))
        self.assertEqual(CONTRACT["scrub"], "UxMotion.scrub")
        self.assertIn("scrub", CONTRACT["player_exports"])

    def test_bind_ir_fields_unchanged(self) -> None:
        plan = scene("essay").bind_to("scroll", "#article").enter("#fig", rise.enter(ms=80)).plan()
        root = plan["root"]
        self.assertEqual(set(root) - {"until", "axis"}, {"kind", "input", "target", "child"})
        self.assertNotIn("whileHover", root)


class TestSoft2PlayerSource(unittest.TestCase):
    def _player(self) -> str:
        from pathlib import Path

        return (Path(__file__).resolve().parents[1] / "static" / "ux-motion-player.js").read_text(
            encoding="utf-8"
        )

    def test_player_applies_morph_d(self) -> None:
        js = self._player()
        self.assertIn("function morphD(", js)
        self.assertIn("recipe.morph", js)
        self.assertIn("morph.d", js)
        self.assertIn("out.d =", js)
        self.assertIn("commitMorphD(", js)
        self.assertIn('el.setAttribute("d"', js)

    def test_offset_path_along_kept(self) -> None:
        js = self._player()
        self.assertIn("el.style.offsetPath", js)
        self.assertIn("recipe.path.d", js)

    def test_scrub_apply_still_present(self) -> None:
        js = self._player()
        self.assertIn("function scrub(planId, progress)", js)
        self.assertIn("function applyTape(", js)
        self.assertIn("function attachScrollLoop(", js)


if __name__ == "__main__":
    unittest.main()
