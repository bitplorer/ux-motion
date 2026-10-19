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

from ux_motion import fade, scene, span_ms, validate_plan

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
        self.assertTrue(got["errors_surfaced"] or got["thrown"], got)

    def test_unfocused_idiomorph_throw_still_replaces_and_surfaces(self) -> None:
        got = _node_player({"probe": "morph"})["unfocused"]
        self.assertFalse(got["same_node"], got)
        self.assertTrue(got["errors_surfaced"] or got["thrown"], got)
