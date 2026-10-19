"""Duration 0 and injectHtml focus. Live checks from item3 motion M1/M2.

The web player is executed with Node (no extra packages) through
``tests/player_harness.js``. Python ``span_ms`` is the schedule reference:
an explicit duration of 0 is a zero span, and a missing duration keeps the
existing default (240 on a track recipe, 320 when a share omits its recipe).
"""

from __future__ import annotations

import json
import shutil
import subprocess
import unittest
from pathlib import Path

from ux_motion import fade, interpret, page, scene, span_ms, tokens, validate_plan
from ux_motion._player import _emit_track

ROOT = Path(__file__).resolve().parents[1]
PLAYER = ROOT / "ux_motion" / "scripts" / "ux-motion-player.js"
HARNESS = ROOT / "tests" / "player_harness.js"


def _plan(node: dict, plan_id: str) -> dict:
    return {
        "v": "1",
        "kind": "plan",
        "id": plan_id,
        "interrupt": "replace",
        "reduced": "honor",
        "engine": "presence",
        "root": {
            "kind": "phase",
            "mode": "wait",
            "stagger_ms": 0,
            "children": [node],
        },
    }


def _zero_track():
    return scene("t").enter("#a", fade.enter().with_duration(0)).play()["ops"][0]["plan"]


def _zero_share():
    return scene("s").share(
        "hero",
        leave="#leave",
        arrive="#arrive",
        recipe=fade.enter().with_duration(0),
    ).play()["ops"][0]["plan"]


def _node_player(probe: dict) -> dict:
    node = shutil.which("node")
    if not node:
        raise AssertionError("node is required to execute ux-motion-player.js")
    proc = subprocess.run(
        [node, str(HARNESS), str(PLAYER)],
        input=json.dumps(probe),
        text=True,
        capture_output=True,
        timeout=20,
        check=False,
    )
    if proc.returncode != 0:
        raise AssertionError(proc.stderr or proc.stdout)
    return json.loads(proc.stdout)


class DurationZeroTests(unittest.TestCase):
    def test_track_span_keeps_explicit_zero(self) -> None:
        self.assertEqual(span_ms(_zero_track()), 0)

    def test_unset_duration_keeps_track_and_share_defaults(self) -> None:
        track = validate_plan(
            _plan(
                {
                    "kind": "track",
                    "target": "#a",
                    "role": "enter",
                    "recipe": {"name": "custom"},
                },
                "unset-track",
            )
        )
        self.assertEqual(track["root"]["children"][0]["recipe"]["duration"], 240)
        self.assertEqual(span_ms(track), 240)
        share = scene("unset-share").share("hero", leave="#leave", arrive="#arrive").plan()
        self.assertEqual(share["root"]["children"][0]["recipe"]["duration"], 320)
        self.assertEqual(span_ms(share), 320)

    def test_share_without_recipe_span_uses_player_default(self) -> None:
        # Author omitted the recipe. span_ms revalidates and stores duration
        # 320 on the plan; the player fallback is the other copy of that 320.
        plan = scene("bare").share("hero", leave="#leave", arrive="#arrive").plan()
        self.assertEqual(span_ms(plan), 320)
        events: list = []
        end = _emit_track(
            {
                "kind": "share",
                "id": "hero",
                "leave": "#leave",
                "arrive": "#arrive",
                "recipe": {"name": "share"},
            },
            0,
            events,
            {},
        )
        self.assertEqual(end, 320)
        self.assertEqual([e.t for e in events if e.event == "end"], [320, 320])

    def test_share_span_keeps_explicit_zero(self) -> None:
        self.assertEqual(span_ms(_zero_share()), 0)

    def test_player_unset_duration_defaults(self) -> None:
        got = _node_player(
            {
                "probe": "duration",
                "plans": {
                    "track": {
                        "sel": "#a",
                        "plan": _plan(
                            {
                                "kind": "track",
                                "target": "#a",
                                "role": "enter",
                                "recipe": {"name": "custom", "from": {"opacity": 0}, "to": {"opacity": 1}},
                            },
                            "js-unset-track",
                        ),
                    },
                    "share": {
                        "sel": "#arrive",
                        "plan": _plan(
                            {"kind": "share", "id": "hero", "leave": "#leave", "arrive": "#arrive"},
                            "js-unset-share",
                        ),
                    },
                },
            }
        )
        self.assertEqual(got["track"], [240])
        self.assertEqual(got["share"], [320])

    def test_player_track_and_share_animate_explicit_zero(self) -> None:
        got = _node_player(
            {
                "probe": "duration",
                "plans": {
                    "track": {"sel": "#a", "plan": _zero_track()},
                    "share": {"sel": "#arrive", "plan": _zero_share()},
                },
            }
        )
        self.assertEqual(got["track"], [0])
        self.assertEqual(got["share"], [0])
        self.assertEqual(got["track"], got["share"])


class InjectHtmlTests(unittest.TestCase):
    def test_idiomorph_throw_keeps_focused_input(self) -> None:
        got = _node_player({"probe": "morph"})["focused"]
        self.assertTrue(got["same_node"], got)
        self.assertTrue(got["focus_kept"], got)
        self.assertEqual(got["input_value"], "typed")
        self._assert_idiomorph_logged(got)

    def test_unfocused_idiomorph_throw_still_replaces_and_surfaces(self) -> None:
        got = _node_player({"probe": "morph"})["unfocused"]
        self.assertFalse(got["same_node"], got)
        self._assert_idiomorph_logged(got)

    def _assert_idiomorph_logged(self, got: dict) -> None:
        logged = " ".join(got["errors_surfaced"])
        self.assertIn("idiomorph failed", logged)
        self.assertIsNone(got["thrown"])


class GapZeroTests(unittest.TestCase):
    def test_default_stagger_gap_stays_40(self) -> None:
        plan = scene("g").stagger_in(".item", fade.enter(ms=10)).plan()
        starts = [e.t for e in interpret(plan, counts={".item": 3}) if e.event == "start"]
        self.assertEqual(starts, [0, 40, 80])

    def test_explicit_stagger_gap_zero(self) -> None:
        plan = scene("g").stagger_in(".item", fade.enter(ms=10), gap_ms=0).plan()
        self.assertEqual(plan["root"]["children"][0]["gap_ms"], 0)
        starts = [e.t for e in interpret(plan, counts={".item": 3}) if e.event == "start"]
        self.assertEqual(starts, [0, 0, 0])

    def test_player_stagger_gap_zero(self) -> None:
        plan = scene("g").stagger_in(".item", fade.enter(ms=10), gap_ms=0).plan()
        plan["reduced"] = "honor"
        got = _node_player(
            {
                "probe": "duration",
                "plans": {"stagger": {"sel": ".item", "plan": plan, "delays": True}},
            }
        )
        self.assertEqual(got["staggerDelays"], [0, 0, 0])

    def test_player_tape_gap_zero(self) -> None:
        plan = (
            scene("tape")
            .bind_to("progress", "#a")
            .stagger_in(".item", fade.enter(ms=100), gap_ms=0)
            .plan()
        )
        plan["reduced"] = "honor"
        got = _node_player(
            {
                "probe": "duration",
                "plans": {"tape": {"sel": ".item", "plan": plan, "scrub": 0.5}},
            }
        )
        self.assertEqual(got["tapeTimes"], [50, 50, 50])


class PageZeroTests(unittest.TestCase):
    def test_page_defaults_keep_token_durations(self) -> None:
        plan = page(leave="#old", arrive="#new")
        durations = {child["role"]: child["recipe"]["duration"] for child in plan["root"]["children"]}
        self.assertEqual(durations["exit"], tokens.ms("exit"))
        self.assertEqual(durations["enter"], tokens.ms("enter"))

    def test_page_explicit_zero_durations(self) -> None:
        plan = page(leave="#old", arrive="#new", exit_ms=0, enter_ms=0)
        durations = {child["role"]: child["recipe"]["duration"] for child in plan["root"]["children"]}
        self.assertEqual(durations["exit"], 0)
        self.assertEqual(durations["enter"], 0)
        self.assertEqual(span_ms(plan), 0)
