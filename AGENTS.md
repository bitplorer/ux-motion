# AGENTS.md — ux-motion

Orientation for humans and agents continuing this package.

**First-time:** [START_HERE.md](START_HERE.md). **Map:** [docs/INDEX.md](docs/INDEX.md).

Read [START_HERE.md](START_HERE.md) then [docs/00-OVERVIEW.md](docs/00-OVERVIEW.md)
then [docs/INDEX.md](docs/INDEX.md). Public names: `ux_motion/__init__.py` `__all__`.
Read [docs/14-CHANNEL-COMPOSITOR.md](docs/14-CHANNEL-COMPOSITOR.md) before changing
`MotionChannel`.

## Layer ownership (hard cut)

The UX stack is a **layered system of specialists**, not a monolith.

| Layer | Owns | Must **not** own |
|-------|------|------------------|
| **ux-dom** | HTML/CSS/JS trees, `Document`, serialize, pure discovery, `uxdom` | Intent, Cap, Result ops, MorphState, motion IR, product CLI |
| **ux-channel** | Intent / Result / Cap / wire / peers / host runtime | HTML trees, CSS |
| **ux-behavior** | Product behavior, Morph/Ref, `@action`, validation | Raw HTML construction, wire codecs |
| **ux-motion** (this repo) | Presence / transition plans as data (IR v1) | Product behavior, DOM construction |
| **ux-compose** | Author composition + product CLI (`uxcompose`) | Re-implementing any specialist |

Channel never learns `transition.*`. `MotionChannel` peels those ops off the Result.
XOR: `morph(T)` XOR `scene.enter(T, html=…)`.

## What not to invent

- Teaching Channel `transition.*` as immortal ops
- A React runtime or CSS framework in this package
- Reusing IR keys with new meanings (v1 is additive only)
- Importing private modules (`ux_motion._ir`, …) from product code
- A sixth stack product
- Pixel-identical physics across engines as a contract (schedule *order* is the contract)

## IR / version law

| Symbol | Value | Meaning |
|--------|-------|---------|
| `API_VERSION` | `"1.3.0"` | Public Python facade |
| `IR_VERSION` / plan `v` | `"1"` | Wire plan shape major. Additive fields only. |
| Player JS `UxMotion.version` | `"1.3.0"` | Aligned with API |

Breaking receivers requires a new plan `v`. Unknown fields must be ignored.

## Tests

```bash
PYTHONPATH=. python -m unittest discover -s tests -v
```

## Docs

Numbered `docs/00`–`docs/14` are the systematic set — keep them; do not flatten
into a monolith. Route via [docs/INDEX.md](docs/INDEX.md). README is a gate only.
