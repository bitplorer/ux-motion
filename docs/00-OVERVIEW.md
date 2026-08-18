# ux_motion 1.2.2 — Complete Overview

**Nothing in this document is optional context.** This is the full product description of the library: what it is, what problem it solves, what it deliberately does not solve, and how every piece fits.

---

## One-sentence definition

**ux_motion** is a pure-Python, server-authored system for composing presence and transition plans that travel over a JSON channel (`ux-channel`-style Result documents) and are executed by a reference player (Python) and a web player (vanilla JavaScript). It is **not** a React library, **not** a CSS framework, and **not** a client-side animation DSL that the browser invents on its own.

---

## Problem it solves

Modern UI animation libraries (Framer Motion, GSAP, Motion One) assume:

1. The component tree lives in the browser.
2. The library owns mount/unmount (e.g. `AnimatePresence`).
3. The developer writes animation intent in JavaScript/TypeScript next to components.

Many server-driven stacks (HTMX-like, LiveView-like, or custom `ux-channel` / `ux-dom` pipelines) violate all three assumptions:

1. The server decides what the DOM becomes.
2. The server does not have a live React fiber tree.
3. The developer wants to author motion in **Python**, next to domain logic.

**ux_motion** turns the Framer Motion insight — *delay unmount until exit finishes; compose enter/exit/stay; interrupt intelligently* — into **data**:

- Server builds a **Plan** (JSON IR v1).
- Plan is emitted as channel ops: `transition.play`, `transition.cancel`, `transition.rewind`.
- Client player executes the plan with WAAPI / View Transitions / FLIP / spring / path.
- Clients that cannot animate receive `send.update` — the same scene as plain DOM ops.

---

## Non-goals (explicit)

| Non-goal | Why |
|---|---|
| Own the React tree | There is no React requirement. |
| Run Python in the browser | Plan is JSON; player is JS or a headless reference. |
| Gesture recognition on the server | Server has no pointer. `bind` only *names* the input; client measures. |
| Replace CSS for static styling | Motion is transitions and presence, not layout design. |
| Guarantee pixel-identical physics across engines | Spring duration is estimated; CSS cubic is approximate. Schedule *order* is the contract. |
| Sanitize user-supplied HTML in `html=` | HTML is trusted server markup (same model as morph). Hosts must not pass raw user HTML. |

---

## Versions

| Symbol | Value | Meaning |
|---|---|---|
| `API_VERSION` | `"1.2.2"` | Public Python facade version |
| `IR_VERSION` / plan field `v` | `"1"` | Wire plan shape major. Additive fields only inside v1. |
| Player JS `UxMotion.version` | `"1.2.2"` | Web player version aligned with API |

**Breaking change rule:** only a new `v` on the plan is allowed to break receivers. Unknown fields must be ignored by receivers. Keys are never reused with new meanings.

---

## Public surface (import only from `ux_motion`)

```python
from ux_motion import (
    # authoring
    scene, track, group, stagger, share, bind, score, cue,
    wait, sequence, parallel,
    # recipes
    fade, rise, slide, scale, blur, none, snap, along, springy,
    # send
    send, play, cancel, rewind, as_update, to_result,
    # inspect
    interpret, explain, frames, span_ms, validate_plan, compile_plan,
    freeze_plan, render_markup, as_html,
    # design system
    tokens, schema, CONTRACT,
    # patterns
    page, modal, toast, list_stagger, shared_page,
    multi_hop_leave, multi_hop_arrive,
    # presence helpers
    stamp, region, Presence,
    # document runtime
    Motion,
    # drop-in HOFs (trees → Scene)
    hop, appear, swap, leave, sheet, notice, staggered, motion,
    # wire
    dumps, loads,
)
```

Product code must **not** import private modules (`ux_motion._ir`, etc.) except in tests that intentionally exercise internals.

---

## Mental model in four objects

1. **Recipe** — how one element moves (from/to opacity, x, y, scale, blur, offset; duration; easing; optional spring; optional path).
2. **Track / Share / Stagger** — *what* moves (a selector + role + recipe, or a named shared identity).
3. **Phase / Group** — *when* relative to siblings (`wait` | `sequence` | `parallel`).
4. **Plan** — the sealed document (`v`, `id`, `root`, interrupt, reduced, engine) that crosses the wire.

`Scene` is a fluent builder that produces a Plan. `send.play(plan)` wraps it in a Result. The player consumes the Result.

---

## Directory layout in this package

```
ux_motion-1.0.0-complete/
├── README.md                 # entry + quick start
├── LICENSE                   # (placeholder — set your license)
├── docs/                     # THIS documentation set
├── ux_motion/                # Python package (importable)
│   ├── __init__.py           # frozen public facade
│   ├── _contract.py          # laws + enumerated surfaces
│   ├── _ir.py                # validator + all kinds
│   ├── _api.py               # Scene + functional constructors
│   ├── _recipes.py           # fade/rise/slide/scale/blur/along/springy
│   ├── _tokens.py            # named duration/easing/distance/spring
│   ├── _ops.py               # play / update / rewind / cancel
│   ├── _adapter.py           # send facade
│   ├── _player.py            # reference interpret / explain / frames
│   ├── _patterns.py          # page/modal/toast/list/shared/multi-hop
│   ├── _schema.py            # JSON Schema of IR v1
│   ├── _presence.py          # stamp / region / Presence map
│   ├── _compile.py           # compile_plan → validate_plan
│   ├── _wire.py              # dumps / loads
│   └── py.typed
├── static/
│   └── ux-motion-player.js   # browser runtime
├── tests/
│   └── test_core.py
└── examples/
    └── minimal.py
```

---

## Quick start (copy-paste)

```python
from ux_motion import scene, fade, rise, send

result = (
    scene("nav")
    .exit("#old", fade.exit())
    .enter("#new", rise.enter())
    .play()
)
# result == {"ok": True, "ops": [{"op": "transition.play", "plan": {...}}]}

# Client with no motion player:
dom_only = scene("nav").exit("#old", fade.exit()).enter("#new", rise.enter()).update()
```

Install for local use:

```bash
export PYTHONPATH=/path/to/ux_motion-1.0.0-complete
python -c "from ux_motion import scene, fade; print(scene('x').enter('#a', fade.enter()).plan()['id'])"
```

---

## Document map

| File | Contents |
|---|---|
| `00-OVERVIEW.md` | This file |
| `01-ARCHITECTURE.md` | Layers, modules, dependency graph, data flow |
| `02-IR-SPEC.md` | Every IR field, kind, enum, validation rule |
| `03-API-REFERENCE.md` | Every public symbol with signatures and effects |
| `04-COMPOSITION-SEMANTICS.md` | wait / sequence / parallel / nested groups — exact rules |
| `05-PLAYER-CONTRACT.md` | Reference player + JS player obligations |
| `06-DESIGN-DECISIONS.md` | Why each design choice; rejected alternatives |
| `07-ENHANCEMENTS.md` | share, bind, score, spring, along, tokens, rewind, patterns |
| `08-WIRE-PROTOCOL.md` | Ops, Result shape, classic projection |
| `09-TESTING.md` | How to run tests; what they guarantee |
| `10-EXAMPLES.md` | End-to-end recipes for real UI cases |
| `11-GLOSSARY.md` | Terms with precise meanings |
| `12-DIAGRAMS.md` | Mermaid at-a-glance diagrams for every concept |
| `13-VERSIONING.md` | Semver policy, IR vs API, release checklist |
