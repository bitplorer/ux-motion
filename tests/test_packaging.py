"""Static JS copies stay identical to package-owned scripts."""

from __future__ import annotations

import re
import unittest
from pathlib import Path

from ux_motion import PLAYER_VERSION, __version__

ROOT = Path(__file__).resolve().parents[1]
JS = (
    "ux-motion-player.js",
    "ux-motion-channel.js",
)


class PackagingTests(unittest.TestCase):
    def test_static_matches_package_scripts(self) -> None:
        for name in JS:
            standalone = (ROOT / "static" / name).read_text(encoding="utf-8")
            packaged = (ROOT / "ux_motion" / "scripts" / name).read_text(encoding="utf-8")
            self.assertEqual(standalone, packaged, name)

    def test_player_version_matches_python(self) -> None:
        self.assertEqual(PLAYER_VERSION, __version__)
        js = (ROOT / "static" / "ux-motion-player.js").read_text(encoding="utf-8")
        self.assertIn(f'version: "{PLAYER_VERSION}"', js)
        self.assertIn(f"web.v{PLAYER_VERSION}", js)
        self.assertTrue(js.rstrip().endswith(");"))

    def test_channel_hook_is_complete(self) -> None:
        js = (ROOT / "static" / "ux-motion-channel.js").read_text(encoding="utf-8")
        self.assertIn("channel:beforeApply", js)
        self.assertIn("channel:afterApply", js)
        self.assertIn("_uxMotion", js)
        self.assertIn("applyOps", js)
        self.assertTrue(js.rstrip().endswith(");"))
        self.assertIsNotNone(re.search(r"transition\.", js))
