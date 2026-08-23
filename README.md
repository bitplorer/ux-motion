# ux_motion 1.3.0

**Server-authored, composable presence and transition plans for Python + JSON channels.**

Pure Python facade. Vanilla JS player. No React. IR v1 additive.

`html=` accepts ux-dom trees. They stay trees until official serialize
(`stamp_tree` + `__render__`) at `dumps` / `send.play` / `Scene.__render__`.

> **New here?** [START_HERE.md](START_HERE.md) (5 minutes).
> **Map:** [docs/INDEX.md](docs/INDEX.md)
> **Overview:** [docs/00-OVERVIEW.md](docs/00-OVERVIEW.md)
> **Contributor / agent:** [CONTRIBUTING.md](CONTRIBUTING.md) · [AGENTS.md](AGENTS.md)

This layer **owns presence/transition plans as data**. It does not own product
behavior or DOM construction.

## Install / use

```bash
pip install ux-motion
# or from this tree:
pip install -e .
python -c "from ux_motion import scene, fade; print(scene('x').enter('#a', fade.enter()).plan()['id'])"
```

Repo: [bitplorer/ux-motion](https://github.com/bitplorer/ux-motion)

### Ownership

| Owns | Does **not** own |
|------|------------------|
| Plan IR v1, recipes, Scene builder | Product `@action` / MorphState (`ux-behavior`) |
| `transition.play` / `cancel` / `rewind` ops | HTML construction / Document (`ux-dom`) |
| Reference player + JS player | Cap crypto / Intent (`ux-channel`) |
| `Motion` / `MotionChannel` Document contributions | Product CLI (`ux-compose`) |

### Audience

| You are… | Start |
|----------|--------|
| **New** | [START_HERE.md](START_HERE.md) |
| **Need every concept** | [docs/00-OVERVIEW.md](docs/00-OVERVIEW.md) · [docs/12-DIAGRAMS.md](docs/12-DIAGRAMS.md) |
| **Changing MotionChannel** | [docs/14-CHANNEL-COMPOSITOR.md](docs/14-CHANNEL-COMPOSITOR.md) |
| **Contributor / agent** | [CONTRIBUTING.md](CONTRIBUTING.md) · [AGENTS.md](AGENTS.md) |
| **Need a map** | [docs/INDEX.md](docs/INDEX.md) |

## 30-second example

```python
from ux_motion import scene, fade, rise

scene("nav").exit("#old", fade.exit()).enter("#new", rise.enter()).play()
```

ux-dom tree on enter, frozen only on the wire:

```python
from ux_dom.dom import section, h1
from ux_motion import appear, rise, swap, Motion, MotionChannel

appear(section(h1("Shop"), id="view"), stagger=".tile").play()
swap("#view", shop_view(), share="vein").play()
rise(product_view(), ms=200)   # family as HOF → Scene

# Player. Add MotionChannel only when Channel applies the Result:
# document.use(Motion(), MotionChannel())
```

`MotionChannel` peels `transition.*` off the Result, lets Channel
idiomorph the slot, then plays the plan. Channel never learns those
ops. Do not also pass `html=` on a target you just morphed
(`morph(T)` XOR `scene.enter(T, html=…)`).

## Documentation

Start at **[START_HERE.md](START_HERE.md)**. Numbered set begins at
**[docs/00-OVERVIEW.md](docs/00-OVERVIEW.md)**.
Visual index: **[docs/12-DIAGRAMS.md](docs/12-DIAGRAMS.md)**.
Channel compositor: **[docs/14-CHANNEL-COMPOSITOR.md](docs/14-CHANNEL-COMPOSITOR.md)**
(read before changing `MotionChannel`).
Full map: **[docs/INDEX.md](docs/INDEX.md)**.

## Tests

```bash
PYTHONPATH=. python -m unittest discover -s tests -v
```

## Package contents

| Path | Role |
|---|---|
| `ux_motion/` | Importable Python package |
| `ux_motion/scripts/ux-motion-player.js` | Package-owned player (`document.use(Motion())`) |
| `ux_motion/scripts/ux-motion-channel.js` | Channel hook (`document.use(MotionChannel())`) |
| `static/ux-motion-player.js` | Same player, standalone URL |
| `static/ux-motion-channel.js` | Same hook, standalone URL |
| `tests/` | Unit tests |
| `docs/` | Exhaustive documentation |
| `examples/minimal.py` | Runnable sample |

## License

MIT
