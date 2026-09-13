# ux-motion — snippets

> **Diátaxis:** how-to · copy-paste patterns from the public API (`__all__` / CLI).
> Map: see this package `docs/INDEX.md`.

Presence and transitions as data (IR v1). Scene builder + JS player.

Every block is meant to run (or to be the exact fragment you drop into a running app). Names are public exports. If code and this page disagree, **code wins**.

**16 snippets** covering install, Scene, Soft 1–3, HOFs, patterns, wire, and the usage patterns that keep layers from leaking.

### Public names in this cookbook

`scene`, `fade`, `rise`, `explain`, `interpret`, `scrub`, `partition_wait`, `wait_clocks`, `send`, `appear`, `swap`, `slide`, `scale`, `springy`, `blur`, `along`, `morph_d`, `page`, `modal`, `toast`, `list_stagger`, `play`, `cancel`, `rewind`, `dumps`, `loads`, `validate_plan`, `freeze_plan`, `PlanError`, `sequence`, `parallel`, `wait`, `tokens`, `snap`, `none`, `frames`, `span_ms`, `Document`, `Motion`, `MotionChannel`, `morph`

## Contents

- [Install](#mo-install)
- [Scene: exit, enter, play](#mo-scene)
- [Shared element (FLIP) + score/cue](#mo-share)
- [Soft 1: scroll tape (`scrub`)](#mo-soft1)
- [Soft 2: SVG path `d` morph](#mo-soft2)
- [Soft 3: wait bags / clocks](#mo-soft3)
- [HOF: appear, swap, recipes](#mo-hof)
- [Named patterns: page, modal, toast, list_stagger](#mo-patterns)
- [cancel / rewind ops](#mo-cancel)
- [dumps / loads / validate_plan / freeze_plan](#mo-dumps)
- [sequence / parallel / wait / group](#mo-phase)
- [Tokens: duration, easing, distance](#mo-tokens)
- [Recipe families](#mo-recipes)
- [explain / interpret / frames / span_ms](#mo-player)
- [Motion + MotionChannel on Document](#mo-channel)
- [Pattern: morph(T) XOR scene.enter(T, html=…)](#mo-pattern-xor)


## Install

### Install

<a id="mo-install"></a>

Pure Python façade. Vanilla JS player. No React. IR v1 additive.

```bash
pip install ux-motion
python -c "from ux_motion import scene, fade; print(scene('x').enter('#a', fade.enter()).plan()['id'])"
```


## Core usage

### Scene: exit, enter, play

<a id="mo-scene"></a>

play() emits transition.play. update() is the no-animation projection. html= trees stay trees until dumps/send.play.

```python
from ux_motion import scene, fade, rise, explain, interpret, send

result = (
    scene("nav")
    .exit("#old", fade.exit())
    .enter("#new", rise.enter())
    .play()
)
print(result["ops"][0]["op"])   # transition.play

plan = scene("nav").exit("#old", fade.exit()).enter("#new", rise.enter()).plan()
print(explain(plan))
for event in interpret(plan):
    print(event)

# Clients that cannot animate:
dom_only = scene("nav").exit("#old", fade.exit()).enter("#new", rise.enter()).update()
```

### Shared element (FLIP) + score/cue

<a id="mo-share"></a>

share() is identity continuity (client measures leave→arrive). score/cue spans HTTP Results.

```python
from ux_motion import scene, fade, rise

scene("pdp").share("hero", leave="#grid-img", arrive="#pdp-img").play()

scene("leave").as_score("checkout", phase="hold").exit("#cart", fade.exit()).play()
# later Result:
# scene("arrive").cue("checkout").enter("#paid", rise.enter()).play()
```

### Soft 1: scroll tape (`scrub`)

<a id="mo-soft1"></a>

`bind_to("scroll", …)` is a 0..1 tape, not a gesture. Player seeks WAAPI from
scroll. Python `scrub` is the logical tape. Gestures are Channel Intent /
Behavior `@action`. Leftover: [../../OWNERSHIP.md](../../OWNERSHIP.md).

From `examples/scroll_scrub.py` / `tests/test_soft1_scrub.py`:

```python
from ux_motion import rise, scrub, scene, span_ms

plan = (
    scene("essay")
    .bind_to("scroll", "#article")
    .enter("#fig", rise.enter(ms=80))
    .plan()
)
start = scrub(plan, 0)
mid = scrub(plan, 0.5)
end = scrub(plan, 1)
# mid.progress == 0.5; mid.t == round(0.5 * mid.span); end.t == span_ms(plan)
# scrub(plan, -2).progress == 0.0; scrub(plan, 4).progress == 1.0
```

JS: `UxMotion.scrub(planId, progress)`. `CONTRACT["scrub"] == "UxMotion.scrub"`.
`bind.input === "drag"` is leftover one-shot play (IR name KEEP).

### Soft 2: SVG path `d` morph

<a id="mo-soft2"></a>

`morph_d` writes recipe `"morph.d"` and `morph.d.{from,to}`. `along` keeps
`path.d` (offset-path). Do not reuse `path`.

From `examples/path_morph.py` / `tests/test_soft2_path_morph.py`:

```python
from ux_motion import along, fade, morph_d, scene

SQUARE = "M0,0 L20,0 L20,20 L0,20 Z"
DIAMOND = "M10,0 L20,10 L10,20 L0,10 Z"

rec = morph_d(SQUARE, DIAMOND, ms=240)
# rec["name"] == "morph.d"; "path" not in rec
fade.enter(ms=80).with_morph_d(SQUARE, DIAMOND)  # name stays fade.enter
along("M0,0 C50,100 150,100 200,0", ms=400)      # path.d; no morph
scene("icon").enter("#blob", rec).plan()
```

Unknown morph keys are ignored. Incomplete `morph.d` (missing from or to)
raises `PlanError`. Rewind swaps from/to.

### Soft 3: wait bags / clocks

<a id="mo-soft3"></a>

Direct track/stagger siblings partition into `exits` / `stays` / `enters`.
Nested kinds start at `t0`. Missing role is enter. `stagger_ms` does not
apply to wait. Not an AnimatePresence dump.

From `examples/wait_complete.py` / `tests/test_soft3_wait.py`:

```python
from ux_motion import fade, partition_wait, scene, wait_clocks

plan = scene("nav").exit("#old", fade.exit(ms=100)).enter("#new", fade.enter(ms=80)).plan()
clock = wait_clocks(plan)
# clock.bags.exits[0]["target"] == "#old"
# clock.exit_end == clock.enter_t == 100; clock.end == 180

bags = partition_wait(
    (
        {"kind": "track", "target": "#x", "recipe": fade.enter(ms=10)},
        {"kind": "track", "target": "#y", "role": "exit", "recipe": fade.exit(ms=10)},
    )
)
# bags.enters[0]["target"] == "#x"; bags.exits[0]["target"] == "#y"
```

JS name: `partitionWait`. `CONTRACT["wait.bags"]` /
`CONTRACT["wait.clocks"]` / `CONTRACT["partition_wait"]`.

### HOF: appear, swap, recipes

<a id="mo-hof"></a>

Do not pass html= on a target you just morphed (morph(T) XOR scene.enter(T, html=…)).

```python
from ux_motion import appear, swap, rise, fade, slide, scale, springy, blur, along, morph_d

appear(section, stagger=".tile").play()          # tree stays a tree
swap("#view", shop_view(), share="vein").play()
rise(product_view(), ms=200)

# Recipe families: fade / rise / slide / scale / snap / springy / blur / along / morph_d / none
scene("x").enter("#a", fade.enter().with_duration(160).with_easing("ease-out")).play()
```

### Named patterns: page, modal, toast, list_stagger

<a id="mo-patterns"></a>

Patterns return frozen plans (not live Scenes). HOFs (appear/swap) return live Scenes. Do not mix the two styles blindly.

```python
from ux_motion import page, modal, toast, list_stagger, play

play(page(leave="#old", arrive="#new"))
play(modal(overlay="#dim", panel="#dialog", open_=True))
play(toast(target="#notice"))
play(list_stagger(selector=".row"))
```

### cancel / rewind ops

<a id="mo-cancel"></a>

Ops are data. The JS player (document.use(Motion())) executes them. MotionChannel peels transition.* off the Result after Channel morphs.

```python
from ux_motion import cancel, rewind, scene, fade

scene("nav").enter("#new", fade.enter()).play()
print(cancel("nav"))    # transition.cancel
print(rewind("nav"))    # transition.rewind
```

### dumps / loads / validate_plan / freeze_plan

<a id="mo-dumps"></a>

IR major is v: "1". Additive fields only. Never reuse keys. html= trees stay trees until dumps / send.play.

```python
from ux_motion import scene, fade, dumps, loads, validate_plan, freeze_plan, PlanError

plan = scene("nav").enter("#new", fade.enter()).plan()
frozen = freeze_plan(plan)          # trees → strings via official __render__
text = dumps(plan)                  # JSON
roundtrip = loads(text)             # validate_plan on the object
print(roundtrip["id"], validate_plan(roundtrip)["v"])  # v is "1"
```

### sequence / parallel / wait / group

<a id="mo-phase"></a>

Nested groups are never flattened. The web player must produce the same start/end order for a given plan.

```python
from ux_motion import scene, fade, rise, sequence, parallel, wait, wait_clocks, play

exit_bit = scene("x").exit("#old", fade.exit()).plan()
enter_bit = scene("x").enter("#new", rise.enter()).plan()

# Data constructors (return frozen plan nodes):
print(sequence(exit_bit, enter_bit)["mode"])
print(parallel(exit_bit, enter_bit)["mode"])
print(wait(exit_bit, enter_bit)["mode"])

plan = scene("nav").exit("#old", fade.exit(ms=100)).enter("#new", rise.enter(ms=80)).plan()
print(wait_clocks(plan).enter_t)

# Scene chaining also has .sequence() / .parallel() for subsequent tracks.
```

### Tokens: duration, easing, distance

<a id="mo-tokens"></a>

Prefer tokens over raw numbers. Hosts may Tokens.override. Recipe defaults already use tokens.ms('enter') / tokens.ease('enter').

```python
from ux_motion import tokens, fade, scene

print(tokens.ms("enter"), tokens.ease("enter"), tokens.distance["sm"])
scene("x").enter("#a", fade.enter().with_duration(tokens.ms("fast"))).play()
```

### Recipe families

<a id="mo-recipes"></a>

Recipes are data. HOFs (appear/rise/swap) wrap them. Do not invent CSS transition strings in product code.

```python
from ux_motion import scene, fade, rise, slide, scale, snap, springy, blur, along, morph_d, none

scene("x").enter("#a", fade.enter())
scene("x").enter("#a", rise.enter(y=16, ms=200))
scene("x").enter("#a", slide.enter(x=24))
scene("x").enter("#a", scale.enter(scale=0.96))
scene("x").enter("#a", snap.enter())
scene("x").enter("#a", springy.enter())
scene("x").enter("#a", blur.enter())
scene("x").enter("#a", along("M0,0 L40,20"))
scene("x").enter("#a", morph_d("M0,0 L20,0 Z", "M0,20 L20,0 Z"))
scene("x").enter("#a", none())   # presence without animation
```

### explain / interpret / frames / span_ms

<a id="mo-player"></a>

Reference player is the decades contract. Time is discrete milliseconds. Use this to test plans without a browser.

```python
from ux_motion import scene, fade, rise, explain, interpret, frames, span_ms

plan = scene("nav").exit("#old", fade.exit()).enter("#new", rise.enter()).plan()
print(explain(plan))
print(span_ms(plan))
for event in interpret(plan):
    print(event.t, event.event, event.target, event.role)
for frame in frames(plan):
    print(frame)
```


## Composition

### Motion + MotionChannel on Document

<a id="mo-channel"></a>

Add MotionChannel only when Channel applies the Result. Isolation: this module does not import ux_channel.

```python
from ux_dom import Document
from ux_motion import Motion, MotionChannel

document = Document(head=[], body=[]).use(Motion(), MotionChannel())
# MotionChannel peels transition.* off the Result (channel:beforeApply),
# lets Channel idiomorph, then plays (channel:afterApply).
# Channel never learns those ops.
```


## Usage patterns

### Pattern: morph(T) XOR scene.enter(T, html=…)

<a id="mo-pattern-xor"></a>

XOR is the law. ux-compose update_with() combines Morph-then-Play by construction.

```python
from ux_motion import scene, rise
from ux_channel import morph  # illustration — product code uses update_with

# LEGAL: Channel morphs #cart, then motion plays a plan *without* html= on #cart
ops = [
    morph("#cart", "<div id='cart'>1</div>"),
    *scene("cart-pop").enter("#cart", rise.enter(ms=160)).play()["ops"],
]

# ILLEGAL: morph(#cart) AND scene.enter("#cart", html=...)
# The player and Channel would race on the same slot.

# Clients that cannot animate: scene(...).update() — no-animation projection.
```
