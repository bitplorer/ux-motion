# Start here — ux-motion

**Audience:** first-time users of this package.
**Promise:** one Plan on the wire in five minutes.
**Time:** ~5 minutes. Facade **1.3.0**, IR v1.

Full product description: [docs/00-OVERVIEW.md](docs/00-OVERVIEW.md).
**Map:** [docs/INDEX.md](docs/INDEX.md). Runnable sample: [examples/minimal.py](examples/minimal.py).
**Cookbook:** [docs/guides/SNIPPETS.md](docs/guides/SNIPPETS.md) — Scene, Soft 1–3, recipes, HOFs, dumps/loads, XOR with morph.
**Soft leftover:** [OWNERSHIP.md](OWNERSHIP.md).

---

## 1. What this layer is (and is not)

**ux-motion** turns presence and transitions into **data**: a Plan (JSON IR v1)
that travels on a channel Result and is executed by a player.

| Owns | Does **not** own |
|------|------------------|
| Plan IR, recipes, Scene, `send.play` | Product behavior / `@action` (`ux-behavior`) |
| JS/Python players | DOM construction (`ux-dom`) |
| `Motion` / `MotionChannel` contributions | Intent / Cap (`ux-channel`) |

Not a React library. Not a CSS framework. Not a client-side DSL the browser invents.

---

## 2. Five minutes

```bash
pip install ux-motion
# or from this tree:
pip install -e .
```

```python
from ux_motion import scene, fade, rise

result = (
    scene("nav")
    .exit("#old", fade.exit())
    .enter("#new", rise.enter())
    .play()
)
# result == {"ok": True, "ops": [{"op": "transition.play", "plan": {...}}]}
print(result["ops"][0]["op"])
```

Success: printed `transition.play`.

Clients that cannot animate:

```python
dom_only = scene("nav").exit("#old", fade.exit()).enter("#new", rise.enter()).update()
```

Inspect without a browser:

```python
from ux_motion import explain, interpret

plan = scene("nav").enter("#new", rise.enter()).plan()
print(explain(plan))
for event in interpret(plan):
    print(event)
```

---

## 3. XOR with morph (do not skip)

On one Result: `morph(T)` XOR `scene.enter(T, html=…)`.
`MotionChannel` peels `transition.*` off the Result so Channel never learns those ops.

```python
# document.use(Motion(), MotionChannel())   # player + channel hook
```

Do not pass `html=` on a target you just morphed.

---

## 3b. Scroll tape (Soft 1 — not a gesture)

`bind_to("scroll", "#article")` is a **0..1 tape**. The player seeks bound
WAAPI from scroll. Python `scrub(plan, p)` is the same logical tape
(`ScrubFrame`). Hosts may call `UxMotion.scrub(planId, progress)`.

From [examples/scroll_scrub.py](examples/scroll_scrub.py):

```python
from ux_motion import rise, scrub, send, scene

plan = (
    scene("essay")
    .bind_to("scroll", "#article")
    .enter("#fig", rise.enter(ms=400))
    .plan()
)
mid = scrub(plan, 0.5)
print(send.play(plan)["ops"][0]["op"])
print(f"progress={mid.progress} t={mid.t} span={mid.span}")
```

`progress` clamps to 0..1 (`t = round(progress * span)`). Same Event set as
`interpret`. `bind.input === "progress"` is the same tape at 0 until the
host seeks. `drag` stays one-shot child play.

Gestures (hover / tap / press / pan / drag, Framer `while*`) are
**Channel Intent / Behavior `@action`**. Leftover teaching:
[OWNERSHIP.md](OWNERSHIP.md).

---

## 3c. Path morph (Soft 2 — not offset-path)

`morph_d(from_d, to_d)` writes recipe `"morph.d"` and `morph.d.{from,to}`.
`along(...)` still owns `path.d` (offset-path). Do not reuse `path`.

From [examples/path_morph.py](examples/path_morph.py):

```python
from ux_motion import morph_d, scene, send

rec = morph_d(
    "M0,0 L20,0 L20,20 L0,20 Z",
    "M10,0 L20,10 L10,20 L0,10 Z",
    ms=320,
)
plan = scene("icon").enter("#blob", rec).plan()
print(send.play(plan)["ops"][0]["op"])
print(plan["root"]["children"][0]["recipe"]["name"])  # morph.d
```

`fade.enter().with_morph_d(from_d, to_d)` is additive (name stays
`fade.enter`). Similar `d` strings only — the player does not normalize
unlike commands. Rewind swaps `from`/`to`.

---

## 3d. Wait clocks (Soft 3 — exit before enter)

`wait` partitions **direct** track/stagger siblings into bags `exits` /
`stays` / `enters`. Other kinds are `nested` and start at `t0`. Inspect
with `partition_wait` / `wait_clocks` (`exit_end`, `stay_end`, `enter_t`).
Missing `role` is enter. Phase `stagger_ms` does not apply to wait.
Not a Framer AnimatePresence dump.

From [examples/wait_complete.py](examples/wait_complete.py):

```python
from ux_motion import fade, scene, wait_clocks

plan = scene("nav").exit("#old", fade.exit(ms=100)).enter("#new", fade.enter(ms=80)).plan()
clock = wait_clocks(plan)
print(plan["root"]["mode"])
print("exit_end", clock.exit_end, "enter_t", clock.enter_t)
# clock.exit_end == clock.enter_t == 100; clock.end == 180
```

---

## 3e. Soft leftover (HOLD)

Soft 1–3 KEEP. Do not add a gesture Soft or Framer-variants dump here.
Leftover: [OWNERSHIP.md](OWNERSHIP.md).

---

## 4. Where next

| Goal | Doc |
|------|-----|
| Complete overview | [docs/00-OVERVIEW.md](docs/00-OVERVIEW.md) |
| Architecture | [docs/01-ARCHITECTURE.md](docs/01-ARCHITECTURE.md) |
| IR fields | [docs/02-IR-SPEC.md](docs/02-IR-SPEC.md) |
| Public symbols | [docs/03-API-REFERENCE.md](docs/03-API-REFERENCE.md) |
| Diagrams | [docs/12-DIAGRAMS.md](docs/12-DIAGRAMS.md) |
| MotionChannel | [docs/14-CHANNEL-COMPOSITOR.md](docs/14-CHANNEL-COMPOSITOR.md) |
| Examples | [docs/10-EXAMPLES.md](docs/10-EXAMPLES.md) · [examples/minimal.py](examples/minimal.py) |
| Contributor / agent | [CONTRIBUTING.md](CONTRIBUTING.md) · [AGENTS.md](AGENTS.md) |
| Soft leftover / layer cut | [OWNERSHIP.md](OWNERSHIP.md) |
| Full map | [docs/INDEX.md](docs/INDEX.md) |
