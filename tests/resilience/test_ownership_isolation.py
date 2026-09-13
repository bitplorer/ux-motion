"""OWN/HARD — ux-motion ownership and plan-contract (library-tailored).

ux-motion owns server-authored presence + transition plans (IR v1).
It is not a product CLI and not an app host. MotionChannel is a contribution.
Soft LOCK: not a gesture library. Soft 1 leftover: scroll-scrub only.
"""
from __future__ import annotations

import importlib
import unittest
from pathlib import Path

from ux_motion import (
    CONTRACT,
    IR_VERSION,
    MotionChannel,
    fade,
    interpret,
    scene,
    validate_plan,
)

ROOT = Path(__file__).resolve().parents[2]
GESTURE_APIS = (
    "whileHover",
    "whileTap",
    "whileFocus",
    "whileDrag",
    "whileInView",
    "onHover",
    "onTap",
    "onPress",
    "onPan",
    "onDrag",
)
GESTURE_EXPORTS = (
    "whileHover",
    "whileTap",
    "whileFocus",
    "whileDrag",
    "whileInView",
    "hover",
    "tap",
    "press",
    "pan",
    "drag",
)
CAP_HOST_MARKERS = (
    "CapHost",
    "mintCap",
    "createCap",
    "HostCap",
    "cap_host",
)


class TestNoProductLifecycleSurface(unittest.TestCase):
    def test_no_product_cli_modules(self):
        for name in (
            "ux_motion.cli",
            "ux_motion.cli.create_app",
            "ux_motion.create_app",
            "ux_motion.serve",
            "ux_motion.deploy",
        ):
            with self.assertRaises((ImportError, ModuleNotFoundError)):
                importlib.import_module(name)


class TestPlanContract(unittest.TestCase):
    def test_ir_contract_versions(self):
        self.assertEqual(IR_VERSION, "1")
        self.assertEqual(CONTRACT["ir"], "1")
        self.assertIn("api", CONTRACT)
        self.assertIn("player", CONTRACT)

    def test_classic_scene_plan_validates_and_interprets(self):
        plan = (
            scene("nav")
            .exit("#old", fade.exit(ms=50))
            .enter("#new", fade.enter(ms=50))
            .plan()
        )
        validate_plan(plan)
        events = interpret(plan)
        self.assertTrue(any(e.target == "#old" for e in events))
        self.assertTrue(any(e.target == "#new" for e in events))


class TestMotionChannelIsContribution(unittest.TestCase):
    def test_channel_hook_kind(self):
        hook = MotionChannel()
        self.assertEqual(hook.plugin_kind, "contribution")
        self.assertEqual(hook.name, "ux_motion.channel")
        self.assertTrue(hook.src.endswith("ux-motion-channel.js"))


class TestSoftLockNoGestureLibrary(unittest.TestCase):
    def test_public_facade_has_no_gesture_exports(self):
        import ux_motion

        names = set(ux_motion.__all__)
        for name in GESTURE_EXPORTS:
            self.assertNotIn(name, names, name)

    def test_player_and_channel_have_no_gesture_apis(self):
        for rel in (
            "static/ux-motion-player.js",
            "static/ux-motion-channel.js",
            "ux_motion/scripts/ux-motion-player.js",
            "ux_motion/scripts/ux-motion-channel.js",
        ):
            src = (ROOT / rel).read_text(encoding="utf-8")
            for name in GESTURE_APIS:
                self.assertNotIn(name, src, f"{rel} {name}")
            self.assertNotIn('addEventListener("pointer', src, rel)
            self.assertNotIn("addEventListener('pointer", src, rel)
            self.assertNotIn('addEventListener("touch', src, rel)
            self.assertNotIn('addEventListener("mousedown', src, rel)
            self.assertNotIn('addEventListener("mousemove', src, rel)

    def test_no_cap_host_invented(self):
        bundle = []
        for rel in (
            "static/ux-motion-player.js",
            "static/ux-motion-channel.js",
            "ux_motion/_channel.py",
        ):
            bundle.append((rel, (ROOT / rel).read_text(encoding="utf-8")))
        for rel, src in bundle:
            for mark in CAP_HOST_MARKERS:
                self.assertNotIn(mark, src, f"{rel} {mark}")
        channel = (ROOT / "static" / "ux-motion-channel.js").read_text(encoding="utf-8")
        self.assertIn("transition.", channel)
        self.assertIn("UxMotion.applyOps", channel)
        self.assertNotIn("transition.scrub", channel)

    def test_soft1_scroll_scrub_is_owned_here(self):
        self.assertEqual(CONTRACT["scrub"], "UxMotion.scrub")
        self.assertIn("scrub", CONTRACT["player_exports"])
        import ux_motion

        self.assertIn("scrub", ux_motion.__all__)
        self.assertIn("ScrubFrame", ux_motion.__all__)
