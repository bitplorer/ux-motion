# ux_motion 1.3.0

**Server-authored, composable presence and transition plans for Python + JSON channels.**

Pure Python facade. Vanilla JS player. No React. IR v1 additive.

`html=` accepts ux-dom trees. They stay trees until official serialize
(`stamp_tree` + `__render__`) at `dumps` / `send.play` / `Scene.__render__`.

## Install / use

```bash
export PYTHONPATH=/path/to/this-directory
python -c "from ux_motion import scene, fade; print(scene('x').enter('#a', fade.enter()).plan()['id'])"
```

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

Start at **[docs/00-OVERVIEW.md](docs/00-OVERVIEW.md)**.  
Visual index: **[docs/12-DIAGRAMS.md](docs/12-DIAGRAMS.md)** (Mermaid, every concept).  
Channel compositor: **[docs/14-CHANNEL-COMPOSITOR.md](docs/14-CHANNEL-COMPOSITOR.md)** (read before changing `MotionChannel`).  
Full map of every design decision, IR field, API symbol, composition rule, and flow diagram is under `docs/`.

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

Set your license in `LICENSE`. Default placeholder is included.
