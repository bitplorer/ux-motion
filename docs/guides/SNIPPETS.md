# ux-motion — snippets

> **Diátaxis:** how-to · copy-paste patterns from the public API (`__all__` / CLI).
> Map: see this package `docs/INDEX.md`.

Presence and transitions as data (IR v1). Scene builder + JS player.

Every block is meant to run (or to be the exact fragment you drop into a running app). Names are public exports. If code and this page disagree, **code wins**.

**13 snippets** covering install, core usage, fail-closed errors, live/async, CLI, and the usage patterns that keep layers from leaking.

### Public names in this cookbook

`scene`, `fade`, `rise`, `explain`, `interpret`, `send`, `appear`, `swap`, `slide`, `scale`, `springy`, `blur`, `along`, `page`, `modal`, `toast`, `list_stagger`, `play`, `cancel`, `rewind`, `dumps`, `loads`, `validate_plan`, `freeze_plan`, `PlanError`, `sequence`, `parallel`, `wait`, `tokens`, `snap`, `none`, `frames`, `span_ms`, `Document`, `Motion`, `MotionChannel`, `morph`

## Contents

- [Install](#mo-install)
- [Scene: exit, enter, play](#mo-scene)
- [Shared element (FLIP) + scroll bind + score/cue](#mo-share)
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

### Shared element (FLIP) + scroll bind + score/cue

<a id="mo-share"></a>

share() is identity continuity (client measures leave→arrive). score/cue spans HTTP Results.

```python
from ux_motion import scene, fade, rise

scene("pdp").share("hero", leave="#grid-img", arrive="#pdp-img").play()

scene("essay").bind_to("scroll", "#article").enter("#fig", rise.enter()).play()

scene("leave").as_score("checkout", phase="hold").exit("#cart", fade.exit()).play()
# later Result:
# scene("arrive").cue("checkout").enter("#paid", rise.enter()).play()
```

### HOF: appear, swap, recipes

<a id="mo-hof"></a>

Do not pass html= on a target you just morphed (morph(T) XOR scene.enter(T, html=…)).

```python
from ux_motion import appear, swap, rise, fade, slide, scale, springy, blur, along

appear(section, stagger=".tile").play()          # tree stays a tree
swap("#view", shop_view(), share="vein").play()
rise(product_view(), ms=200)

# Recipe families: fade / rise / slide / scale / snap / springy / blur / along / none
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
from ux_motion import scene, fade, rise, sequence, parallel, wait, play

exit_bit = scene("x").exit("#old", fade.exit()).plan()
enter_bit = scene("x").enter("#new", rise.enter()).plan()

# Data constructors (return frozen plan nodes):
print(sequence(exit_bit, enter_bit)["mode"])
print(parallel(exit_bit, enter_bit)["mode"])
print(wait(exit_bit, enter_bit)["mode"])

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
from ux_motion import scene, fade, rise, slide, scale, snap, springy, blur, along, none

scene("x").enter("#a", fade.enter())
scene("x").enter("#a", rise.enter(y=16, ms=200))
scene("x").enter("#a", slide.enter(x=24))
scene("x").enter("#a", scale.enter(scale=0.96))
scene("x").enter("#a", snap.enter())
scene("x").enter("#a", springy.enter())
scene("x").enter("#a", blur.enter())
scene("x").enter("#a", along.enter())
scene("x").enter("#a", none.enter())   # presence without animation
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
