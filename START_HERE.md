# Start here — ux-motion 1.3.0

**Audience:** first-time users of this package.
**Promise:** one Plan on the wire in five minutes.
**Time:** ~5 minutes.

Full product description: [docs/00-OVERVIEW.md](docs/00-OVERVIEW.md).
Map: [docs/INDEX.md](docs/INDEX.md). Runnable sample: [examples/minimal.py](examples/minimal.py).

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
| Full map | [docs/INDEX.md](docs/INDEX.md) |
