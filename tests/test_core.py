"""Core facade, schedule, and enhancement tests."""

from __future__ import annotations

import json
import unittest

from ux_motion import (
    API_VERSION,
    CONTRACT,
    IR_VERSION,
    PLAYER_VERSION,
    __version__,
    OP_PLAY,
    OP_REWIND,
    Motion,
    PlanError,
    along,
    as_update,
    bind,
    compile_plan,
    cue,
    dumps,
    explain,
    fade,
    frames,
    interpret,
    loads,
    modal,
    page,
    rise,
    scene,
    schema,
    score,
    send,
    share,
    slide,
    span_ms,
    springy,
    tokens,
    validate_plan,
    wait,
)


class CoreTests(unittest.TestCase):
    def test_versions(self) -> None:
        self.assertEqual(API_VERSION, "1.2.0")
        self.assertEqual(__version__, "1.2.0")
        self.assertEqual(PLAYER_VERSION, "1.2.0")
        self.assertEqual(IR_VERSION, "1")
        self.assertEqual(CONTRACT["api"], "1.2.0")
        self.assertEqual(CONTRACT["player"], "1.2.0")
        self.assertEqual(CONTRACT["ir"], "1")

    def test_classic_wait(self) -> None:
        plan = scene("nav").exit("#old", fade.exit(ms=100)).enter("#new", fade.enter(ms=100)).plan()
        ev = interpret(plan)
        old_end = next(e.t for e in ev if e.target == "#old" and e.event == "end")
        new_start = next(e.t for e in ev if e.target == "#new" and e.event == "start")
        self.assertGreaterEqual(new_start, old_end)

    def test_share(self) -> None:
        plan = scene("pdp").share("hero", leave="#grid-img", arrive="#pdp-img").plan()
        self.assertEqual(plan["root"]["children"][0]["kind"], "share")
        ev = interpret(plan)
        self.assertTrue(any(e.role == "share-leave" for e in ev))
        self.assertTrue(any(e.role == "share-arrive" for e in ev))
        ops = as_update(plan)
        self.assertTrue(any(o.get("target") == "#pdp-img" for o in ops))

    def test_bind(self) -> None:
        plan = scene("essay").bind_to("scroll", "#article").enter("#fig", rise.enter(ms=80)).plan()
        self.assertEqual(plan["root"]["kind"], "bind")
        self.assertEqual(plan["root"]["input"], "scroll")
        ev = interpret(plan)
        self.assertTrue(any("@bind:" in e.target for e in ev))

    def test_score_and_cue(self) -> None:
        leave = scene("leave").as_score("checkout", phase="hold").exit("#cart", fade.exit(ms=80)).plan()
        self.assertEqual(leave["root"]["kind"], "score")
        arrive = scene("arrive").also(cue("checkout"), wait(
            {"kind": "track", "target": "#pay", "role": "enter", "after": "keep", "recipe": rise.enter(ms=80)}
        )).plan()
        # cue alone is valid as a root child via also
        self.assertTrue(arrive)

    def test_spring_recipe(self) -> None:
        rec = springy(preset="gentle")
        self.assertEqual(rec["engine"], "spring")
        self.assertIn("stiffness", rec["spring"])
        plan = scene("s").enter("#x", rec).engine("spring").plan()
        self.assertEqual(plan["engine"], "spring")

    def test_along_path(self) -> None:
        rec = along("M0,0 C50,100 150,100 200,0", ms=400)
        self.assertIn("path", rec)
        self.assertEqual(rec["path"]["d"][:2], "M0")

    def test_tokens(self) -> None:
        self.assertGreater(tokens.ms("enter"), 0)
        self.assertIn("cubic-bezier", tokens.ease("enter"))
        self.assertIn("snappy", tokens.as_dict()["spring"])

    def test_rewind(self) -> None:
        plan = scene("rw").enter("#a", fade.enter(ms=100)).plan()
        doc = send.rewind(plan)
        self.assertEqual(doc["ops"][0]["op"], OP_REWIND)
        inv = doc["ops"][0]["plan"]
        role = inv["root"]["children"][0]["role"]
        self.assertEqual(role, "exit")

    def test_patterns(self) -> None:
        p = page(leave="#a", arrive="#b")
        validate_plan(p)
        m = modal(overlay="#ov", panel="#pn")
        validate_plan(m)

    def test_reduce_tree(self) -> None:
        plan = (
            scene("r")
            .enter("#x", fade.enter(ms=200))
            .when_reduce({"kind": "track", "target": "#x", "role": "enter", "after": "keep", "recipe": fade.enter(ms=0)})
            .plan()
        )
        self.assertEqual(plan["reduced"], "swap")
        self.assertIn("reduce_tree", plan)

    def test_frames_svg(self) -> None:
        plan = scene("f").exit("#a", fade.exit(ms=80)).enter("#b", fade.enter(ms=80)).plan()
        svg = frames(plan)
        self.assertIn("<svg", svg)
        self.assertIn("#a", svg)

    def test_schema(self) -> None:
        s = schema()
        self.assertEqual(s["properties"]["v"]["const"], "1")
        self.assertIn("share", s["definitions"]["node"]["properties"]["kind"]["enum"])

    def test_send_play_update(self) -> None:
        plan = scene("p").enter("#x", fade.enter()).plan()
        self.assertEqual(send.play(plan)["ops"][0]["op"], OP_PLAY)
        self.assertNotEqual(send.update(plan)["ops"][0]["op"], OP_PLAY)

    def test_roundtrip(self) -> None:
        plan = scene("rt").share("h", leave="#a", arrive="#b").enter("#c", slide.enter()).plan()
        again = loads(dumps(plan))
        self.assertEqual(again["id"], "rt")

    def test_explain(self) -> None:
        text = explain(scene("ex").exit("#a", fade.exit(ms=50)).enter("#b", fade.enter(ms=50)).plan())
        self.assertIn("#a", text)

    def test_motion_namespace(self) -> None:
        node = Motion.share("h", leave="#a", arrive="#b")
        self.assertEqual(node["kind"], "share")

    def test_as_html_coerces_renderable(self) -> None:
        from ux_motion import as_html

        class FakeDom:
            def __render__(self, pretty=True):
                return "<section id=\"view\">ok</section>"

        self.assertEqual(as_html(None), "")
        self.assertEqual(as_html("<b>x</b>"), "<b>x</b>")
        self.assertIn('id="view"', as_html(FakeDom()))
        tree = FakeDom()
        plan = scene("dom").enter("#view", fade.enter(ms=40), html=tree).plan()
        live = plan["root"]["children"][0]["html"]
        self.assertIs(live, tree)
        from ux_motion import freeze_plan, dumps

        frozen = freeze_plan(plan)
        html = frozen["root"]["children"][0]["html"]
        self.assertIsInstance(html, str)
        self.assertIn("<section", html)
        self.assertIn("<section", dumps(plan))
        self.assertIs(plan["root"]["children"][0]["html"], tree)

    def test_unknown_kind_rejected(self) -> None:
        with self.assertRaises(PlanError):
            validate_plan({"v": "1", "kind": "plan", "id": "x", "root": {"kind": "wormhole"}})

    def test_duration_cap(self) -> None:
        with self.assertRaises(PlanError):
            scene("long").enter("#x", fade.enter(ms=200_000)).plan()


class PropertySmoke(unittest.TestCase):
    def test_share_span_positive(self) -> None:
        plan = scene("s").share("h", leave="#a", arrive="#b").plan()
        self.assertGreater(span_ms(plan), 0)

    def test_bind_preserves_child_schedule(self) -> None:
        plan = scene("b").bind_to("drag", "#sheet").enter("#sheet", slide.enter(ms=100)).plan()
        self.assertGreaterEqual(span_ms(plan), 100)


if __name__ == "__main__":
    unittest.main()
