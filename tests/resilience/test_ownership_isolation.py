"""OWN/HARD — ux-motion ownership and plan-contract (library-tailored).

ux-motion owns server-authored presence + transition plans (IR v1).
It is not a product CLI and not an app host. MotionChannel is a contribution.
"""
from __future__ import annotations

import importlib
import unittest

from ux_motion import (
    CONTRACT,
    IR_VERSION,
    MotionChannel,
    fade,
    interpret,
    scene,
    validate_plan,
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
