"""Drop-in higher-order functions: trees stay until official serialize."""

from __future__ import annotations

import unittest

from ux_motion import (
    Scene,
    Recipe,
    appear,
    css_target,
    fade,
    freeze_plan,
    hop,
    leave,
    motion,
    notice,
    rise,
    sheet,
    staggered,
    swap,
)


class FakeDom:
    def __init__(self, markup: str = '<section id="view">ok</section>', *, uid: str = "view") -> None:
        self.markup = markup
        self.attributes = {"id": uid}
        self.children: list = []
        self.renders = 0

    def __render__(self, pretty=True):
        self.renders += 1
        return self.markup


class HofTests(unittest.TestCase):
    def test_css_target_from_tree_and_string(self) -> None:
        self.assertEqual(css_target(FakeDom()), "#view")
        self.assertEqual(css_target("view"), "#view")
        self.assertEqual(css_target("#view"), "#view")
        self.assertEqual(css_target(".tile"), ".tile")

    def test_appear_keeps_tree(self) -> None:
        tree = FakeDom()
        sc = appear(tree)
        self.assertIsInstance(sc, Scene)
        plan = sc.plan()
        self.assertIs(plan["root"]["children"][0]["html"], tree)
        self.assertEqual(plan["root"]["children"][0]["target"], "#view")
        self.assertEqual(tree.renders, 0)
        frozen = freeze_plan(plan)
        self.assertIsInstance(frozen["root"]["children"][0]["html"], str)
        self.assertGreaterEqual(tree.renders, 1)

    def test_appear_into_override(self) -> None:
        tree = FakeDom(uid="shop")
        plan = appear(tree, into="#view").plan()
        self.assertEqual(plan["root"]["children"][0]["target"], "#view")
        self.assertIs(plan["root"]["children"][0]["html"], tree)

    def test_swap_stagger_and_share(self) -> None:
        tree = FakeDom()
        plan = swap("#view", tree, stagger=".tile", share="vein").plan()
        kinds = [n["kind"] for n in plan["root"]["children"]]
        self.assertIn("share", kinds)
        self.assertIn("stagger", kinds)
        enter = next(n for n in plan["root"]["children"] if n.get("role") == "enter")
        self.assertIs(enter["html"], tree)
        share = next(n for n in plan["root"]["children"] if n["kind"] == "share")
        self.assertEqual(share["leave"], "#thumb-vein")
        stagger = next(n for n in plan["root"]["children"] if n["kind"] == "stagger")
        self.assertEqual(stagger["selector"], "#view .tile")

    def test_family_call_is_hof(self) -> None:
        tree = FakeDom()
        rec = rise(ms=180)
        self.assertIsInstance(rec, Recipe)
        self.assertEqual(rec["duration"], 180)
        sc = rise(tree, ms=180)
        self.assertIsInstance(sc, Scene)
        plan = sc.plan()
        self.assertIs(plan["root"]["children"][0]["html"], tree)
        self.assertEqual(plan["root"]["children"][0]["recipe"]["duration"], 180)
        self.assertEqual(plan["id"], "rise")

    def test_leave_and_sheet(self) -> None:
        plan = leave("#view").plan()
        self.assertEqual(plan["root"]["children"][0]["role"], "exit")
        ov = FakeDom(uid="overlay")
        panel = FakeDom(uid="sheet-panel")
        open_plan = sheet(ov, panel, open_=True).plan()
        roles = [n.get("role") for n in open_plan["root"]["children"]]
        self.assertEqual(roles.count("enter"), 2)
        close_plan = sheet("#overlay", "#sheet-panel", open_=False).plan()
        self.assertTrue(all(n.get("role") == "exit" for n in close_plan["root"]["children"]))

    def test_notice_finds_inner_toast(self) -> None:
        inner = FakeDom('<div id="toast-3">hi</div>', uid="toast-3")
        tray = FakeDom('<div id="toasts"></div>', uid="toasts")
        tray.children = [inner]
        plan = notice(tray).plan()
        self.assertEqual(plan["root"]["children"][0]["target"], "#toast-3")
        self.assertIs(plan["root"]["children"][0]["html"], tray)

    def test_hop_pair(self) -> None:
        leave_plan = hop.leave("co", "#step-ship").plan()
        self.assertEqual(leave_plan["root"]["kind"], "score")
        arrive_plan = hop.arrive("co", "#step-pay").plan()
        self.assertTrue(arrive_plan)

    def test_decorator(self) -> None:
        @motion(stagger=".tile")
        def shop():
            return FakeDom()

        sc = shop()
        self.assertIsInstance(sc, Scene)
        self.assertEqual(sc.plan()["id"], "shop")
        self.assertIs(shop.view, shop.__wrapped__)
        self.assertIsInstance(shop.view(), FakeDom)

    def test_staggered_host_tree(self) -> None:
        tree = FakeDom()
        plan = staggered(tree, ".tile").plan()
        kinds = [n["kind"] for n in plan["root"]["children"]]
        self.assertIn("stagger", kinds)

    def test_play_freezes(self) -> None:
        tree = FakeDom()
        result = swap("#view", tree).play()
        html = result["ops"][0]["plan"]["root"]["children"][0]["html"]
        self.assertEqual(html, tree.markup)
        self.assertIsInstance(html, str)


class UxDomHofTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        try:
            from ux_dom.dom import h1, section
        except ImportError:
            raise unittest.SkipTest("ux-dom not installed")
        cls.section = section
        cls.h1 = h1

    def test_real_tree_drop_in(self) -> None:
        tree = self.section(self.h1("Shop"), id="view")
        sc = appear(tree, stagger=".tile")
        plan = sc.plan()
        self.assertIs(plan["root"]["children"][0]["html"], tree)
        frozen = freeze_plan(sc)
        html = frozen["root"]["children"][0]["html"]
        self.assertIn("Shop", html)
        self.assertIn('id="view"', html)

    def test_rise_on_real_tree(self) -> None:
        tree = self.section(self.h1("Salt"), id="view")
        result = rise(tree, ms=200).play()
        html = result["ops"][0]["plan"]["root"]["children"][0]["html"]
        self.assertIn("Salt", html)


if __name__ == "__main__":
    unittest.main()
