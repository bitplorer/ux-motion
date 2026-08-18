# ux_motion 1.0.0

**Server-authored, composable presence and transition plans for Python + JSON channels.**

Pure Python facade. Vanilla JS player. No React. IR v1 additive.

## Install / use

```bash
export PYTHONPATH=/path/to/this/directory
python -c "from ux_motion import scene, fade; print(scene('x').enter('#a', fade.enter()).plan()['id'])"
```

## 30-second example

```python
from ux_motion import scene, fade, rise

scene("nav").exit("#old", fade.exit()).enter("#new", rise.enter()).play()
```

## Documentation

Start at **[docs/00-OVERVIEW.md](docs/00-OVERVIEW.md)**.  
Visual index: **[docs/12-DIAGRAMS.md](docs/12-DIAGRAMS.md)** (Mermaid, every concept).  
Full map of every design decision, IR field, API symbol, composition rule, and flow diagram is under `docs/`.

## Tests

```bash
PYTHONPATH=. python -m unittest discover -s tests -v
```

## Package contents

| Path | Role |
|---|---|
| `ux_motion/` | Importable Python package |
| `static/ux-motion-player.js` | Browser player |
| `tests/` | Unit tests |
| `docs/` | Exhaustive documentation |
| `examples/minimal.py` | Runnable sample |

## License

Set your license in `LICENSE`. Default placeholder is included.
