"""OWN — motion does not own product lifecycle."""
from __future__ import annotations

import importlib
import unittest


class TestNoProductCliSurface(unittest.TestCase):
    def test_no_create_app(self):
        for name in ("ux_motion.cli.create_app", "ux_motion.create_app"):
            with self.assertRaises((ImportError, ModuleNotFoundError)):
                importlib.import_module(name)
