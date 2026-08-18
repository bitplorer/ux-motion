"""ux-dom render-model integration: trees stay until official serialize."""

from __future__ import annotations

import json
import unittest

from ux_motion import (
    fade,
    freeze_plan,
    rise,
    scene,
    send,
    dumps,
)


class FakeDom:
    def __init__(self, markup: str = '<section id="view">ok</section>') -> None:
        self.markup = markup
        self.renders = 0

    def __render__(self, pretty=True):
        self.renders += 1
        return self.markup


class RenderModelTests(unittest.TestCase):
    def test_enter_keeps_tree(self) -> None:
        tree = FakeDom()
        sc = scene("nav").enter("#view", fade.enter(ms=40), html=tree)
        plan = sc.plan()
        self.assertIs(plan["root"]["children"][0]["html"], tree)
        self.assertEqual(tree.renders, 0)

    def test_freeze_calls_official_render(self) -> None:
        tree = FakeDom()
        plan = scene("nav").enter("#view", fade.enter(ms=40), html=tree).plan()
        frozen = freeze_plan(plan)
        self.assertEqual(tree.renders, 1)
        self.assertEqual(frozen["root"]["children"][0]["html"], tree.markup)
        self.assertIs(plan["root"]["children"][0]["html"], tree)

    def test_send_play_freezes_on_the_wire(self) -> None:
        tree = FakeDom()
        result = scene("nav").enter("#view", fade.enter(ms=40), html=tree).play()
        html = result["ops"][0]["plan"]["root"]["children"][0]["html"]
        self.assertEqual(html, tree.markup)
        self.assertGreaterEqual(tree.renders, 1)

    def test_scene_render_carries_all_information(self) -> None:
        tree = FakeDom('<article id="view"><h1>VEIN</h1></article>')
        sc = scene("nav").enter("#view", rise.enter(ms=80), html=tree)
        rendered = sc.__render__(pretty=False)
        self.assertIn('type="application/ux-motion+json"', rendered)
        self.assertIn("data-ux-motion", rendered)
        inner = rendered.split(">", 1)[1].rsplit("</script>", 1)[0]
        payload = json.loads(inner.replace("\\u003c", "<"))
        self.assertEqual(payload["kind"], "plan")
        self.assertEqual(payload["id"], "nav")
        self.assertIn("<article", payload["root"]["children"][0]["html"])
        self.assertIn("VEIN", payload["root"]["children"][0]["html"])
        self.assertEqual(payload["root"]["children"][0]["recipe"]["name"], "rise.enter")

    def test_str_and_html_dunders(self) -> None:
        sc = scene("x").enter("#a", fade.enter(ms=20), html=FakeDom())
        self.assertIn("application/ux-motion+json", str(sc))
        self.assertIn("application/ux-motion+json", sc.__html__())

    def test_dumps_accepts_scene(self) -> None:
        sc = scene("x").enter("#a", fade.enter(ms=20), html=FakeDom("<b>q</b>"))
        text = dumps(sc)
        data = json.loads(text)
        self.assertEqual(data["id"], "x")
        self.assertEqual(data["root"]["children"][0]["html"], "<b>q</b>")


class UxDomTreeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        try:
            from ux_dom.dom import div, h1, section
        except ImportError:
            raise unittest.SkipTest("ux-dom not installed")
        cls.div = div
        cls.h1 = h1
        cls.section = section

    def test_real_tree_stays_until_wire(self) -> None:
        tree = self.section(self.h1("Salt"), id="view")
        sc = scene("shop").enter("#view", fade.enter(ms=40), html=tree)
        plan = sc.plan()
        self.assertIs(plan["root"]["children"][0]["html"], tree)
        frozen = freeze_plan(plan)
        html = frozen["root"]["children"][0]["html"]
        self.assertIsInstance(html, str)
        self.assertIn("Salt", html)
        self.assertIn("id=\"view\"", html)

    def test_scene_in_tree_serializes_via_walk(self) -> None:
        tree = self.section("Hi", id="view")
        sc = scene("embed").enter("#view", fade.enter(ms=40), html=tree)
        host = self.div(sc, id="host")
        html = host.__render__(pretty=False)
        self.assertIn("application/ux-motion+json", html)
        self.assertIn("embed", html)
        self.assertIn("Hi", html)

    def test_document_use_motion(self) -> None:
        from ux_dom import Document
        from ux_motion import Motion

        doc = Document(head=[], body=[]).use(Motion())
        names = [getattr(rt, "name", None) for rt in doc.runtimes()]
        self.assertIn("ux_motion", names)
        head = Motion().document_head()
        self.assertTrue(head)
        markup = head[0].__render__(pretty=False)
        self.assertIn("ux-motion-player.js", markup)


if __name__ == "__main__":
    unittest.main()
