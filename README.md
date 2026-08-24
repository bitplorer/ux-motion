# ux-motion

[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

Server-authored, composable presence and transition plans for Python + JSON channels.

Pure Python facade. Vanilla JS player. No React. IR v1 additive.

`html=` accepts ux-dom trees. They stay trees until official serialize (`stamp_tree` + `__render__`) at `dumps` / `send.play` / `Scene.__render__`.

This layer **owns presence/transition plans as data**. It does not own product behavior or DOM construction.

| Layer | Name |
|-------|------|
| **PyPI / pip** | `ux-motion` |
| **Import** | `ux_motion` |
| **CLI** | *none (library)* |
| **Version** | `1.3.0` |
| **Python** | ≥ 3.10 |
| **License** | [MIT](LICENSE) |

## Table of Contents

- [Install](#install)
- [Usage](#usage)
- [Ownership](#ownership)
- [Audience](#audience)
- [Documentation](#documentation)
- [API](#api)
- [Package contents](#package-contents)
- [Tests](#tests)
- [Security](#security)
- [Contributing](#contributing)
- [License](#license)

## Install

```bash
pip install ux-motion
# or from this tree:
pip install -e .
python -c "from ux_motion import scene, fade; print(scene('x').enter('#a', fade.enter()).plan()['id'])"
```

Repo: [bitplorer/ux-motion](https://github.com/bitplorer/ux-motion)

## Usage

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

`MotionChannel` peels `transition.*` off the Result, lets Channel idiomorph the slot, then plays the plan. Channel never learns those ops. Do not also pass `html=` on a target you just morphed (`morph(T)` XOR `scene.enter(T, html=…)`).

Clients that cannot animate:

```python
dom_only = scene("nav").exit("#old", fade.exit()).enter("#new", rise.enter()).update()
```

Runnable sample: [examples/minimal.py](examples/minimal.py). Five-minute path: [START_HERE.md](START_HERE.md).

## Ownership

| Owns | Does **not** own |
|------|------------------|
| Plan IR v1, recipes, Scene builder | Product `@action` / MorphState (`ux-behavior`) |
| `transition.play` / `cancel` / `rewind` ops | HTML construction / Document (`ux-dom`) |
| Reference player + JS player | Cap crypto / Intent (`ux-channel`) |
| `Motion` / `MotionChannel` Document contributions | Product CLI (`ux-compose`) |

## Audience

| You are… | Start |
|----------|--------|
| **New** | [START_HERE.md](START_HERE.md) |
| **Need every concept** | [docs/00-OVERVIEW.md](docs/00-OVERVIEW.md) · [docs/12-DIAGRAMS.md](docs/12-DIAGRAMS.md) |
| **Changing MotionChannel** | [docs/14-CHANNEL-COMPOSITOR.md](docs/14-CHANNEL-COMPOSITOR.md) |
| **Contributor / agent** | [CONTRIBUTING.md](CONTRIBUTING.md) · [AGENTS.md](AGENTS.md) |
| **Need a map** | [docs/INDEX.md](docs/INDEX.md) |
| **Security reviewer** | [SECURITY.md](SECURITY.md) |
| **Questions** | [SUPPORT.md](SUPPORT.md) |

## Documentation

Family contract: [docs/DOCUMENTATION.md](docs/DOCUMENTATION.md).

Start at **[START_HERE.md](START_HERE.md)**. Numbered set begins at **[docs/00-OVERVIEW.md](docs/00-OVERVIEW.md)**. Full map: **[docs/INDEX.md](docs/INDEX.md)**.

| Diátaxis | Canonical |
|----------|-----------|
| Tutorial | [START_HERE.md](START_HERE.md) · [docs/10-EXAMPLES.md](docs/10-EXAMPLES.md) |
| How-to | [docs/guides/SNIPPETS.md](docs/guides/SNIPPETS.md) · [docs/09-TESTING.md](docs/09-TESTING.md) · [docs/14-CHANNEL-COMPOSITOR.md](docs/14-CHANNEL-COMPOSITOR.md) · [docs/07-ENHANCEMENTS.md](docs/07-ENHANCEMENTS.md) |
| Reference | [docs/02-IR-SPEC.md](docs/02-IR-SPEC.md) · [docs/03-API-REFERENCE.md](docs/03-API-REFERENCE.md) · [docs/08-WIRE-PROTOCOL.md](docs/08-WIRE-PROTOCOL.md) |
| Explanation | [docs/00-OVERVIEW.md](docs/00-OVERVIEW.md) · [docs/01-ARCHITECTURE.md](docs/01-ARCHITECTURE.md) · [docs/06-DESIGN-DECISIONS.md](docs/06-DESIGN-DECISIONS.md) |

Do not cite `Moved (Phase 2 Diátaxis)` stubs as canonical.

## API

Public names are `ux_motion.__all__`. The names product code should hold:

| Export | Role |
|--------|------|
| `scene`, `Scene` | Fluent plan builder |
| `fade`, `rise`, `slide`, `scale`, `blur`, `snap`, `springy`, `along`, `none` | Recipes |
| `appear`, `leave`, `swap`, `sheet`, `notice`, `staggered`, `hop` | Higher-order helpers |
| `play`, `cancel`, `rewind`, `to_result` | Ops onto a Result |
| `Motion`, `MotionChannel` | Document contributions |
| `dumps`, `loads`, `compile_plan`, `validate_plan`, `freeze_plan` | Wire / IR |
| `explain`, `interpret`, `frames` | Inspect a plan without a browser |
| `share`, `bind`, `score`, `cue`, `stagger`, `sequence`, `parallel` | Composition |

IR major is `v: "1"`. Additive fields only. Never reuse keys. Full signatures: [docs/03-API-REFERENCE.md](docs/03-API-REFERENCE.md).

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

## Tests

```bash
PYTHONPATH=. python -m unittest discover -s tests -v
```

## Security

Plans are data. HTML in `html=` is the host’s escaping / CSP problem. This layer does not mint Caps. See [SECURITY.md](SECURITY.md).

## Contributing

PRs are welcome. Read [CONTRIBUTING.md](CONTRIBUTING.md) and [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md). Questions: [SUPPORT.md](SUPPORT.md). Governance: [GOVERNANCE.md](GOVERNANCE.md). History: [CHANGELOG.md](CHANGELOG.md).

## License

MIT — see [LICENSE](LICENSE). Copyright ux_motion contributors.
