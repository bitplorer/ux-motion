# Contributing

**First-time:** [START_HERE.md](START_HERE.md). **Map:** [docs/INDEX.md](docs/INDEX.md). **Agent contract:** [AGENTS.md](AGENTS.md).

## Setup

Python **3.10+**. Layout: top-level `ux_motion/` (not `src/`).

```bash
pip install -e .
PYTHONPATH=. python -c "from ux_motion import scene, fade; print(scene('x').enter('#a', fade.enter()).plan()['id'])"
```

## Quality gate

```bash
PYTHONPATH=. python -m unittest discover -s tests -v
```

Runnable sample: `PYTHONPATH=. python examples/minimal.py`.

## Laws

See [AGENTS.md](AGENTS.md) and [docs/06-DESIGN-DECISIONS.md](docs/06-DESIGN-DECISIONS.md).

- Public imports from `ux_motion` only (`__all__` in `ux_motion/__init__.py`).
- IR v1 is additive. Never reuse keys. New major = new plan `v`.
- `MotionChannel` changes require reading [docs/14-CHANNEL-COMPOSITOR.md](docs/14-CHANNEL-COMPOSITOR.md).
- XOR with morph stays enforced. Do not teach Channel `transition.*`.
- This layer does not own product behavior or DOM construction.

## Docs

| File | May contain | Must not contain |
|------|-------------|------------------|
| `README.md` | Gate | Full API laundry list as primary form |
| `START_HERE.md` | 5-minute first success | Exhaustive IR field list |
| `docs/00`–`14` | Numbered systematic set | Duplicate the gate |
| `docs/INDEX.md` | Audience + Diátaxis routing | Empty new folder trees |

Keep the numbered docs. Assign mode in INDEX; do not rename in Phase 1.

## Pull requests

- Feature branches. Never commit directly to `main`. Never force-push `main`.
- IR field additions need `docs/02-IR-SPEC.md` + tests in the same PR.
- Player JS and Python facade versions stay aligned (`1.3.0` as of this HEAD).
