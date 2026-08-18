# Player Contract

Two players exist. They share one contract: **the schedule**.

## Reference player (Python) — source of truth

Module: `ux_motion._player`

| Function | Obligation |
|---|---|
| `interpret(plan, counts=None)` | Pure; deterministic; returns sorted `Event` list |
| `span_ms` | `max(event.t)` or 0 |
| `explain` | Human-readable schedule text |
| `frames` | SVG strip for CI (no browser) |

Event sort key: `(t, 0 if start else 1, target, role)`.

Stagger without `counts` entry uses **N=3** for logical expansion. Tests that care about N must pass `counts`.

## Web player (JavaScript) — physical execution

File: `static/ux-motion-player.js`  
Global: `window.UxMotion`

```javascript
UxMotion.play(plan)           // Promise
UxMotion.applyOp(op)          // Promise
UxMotion.applyOps(ops)        // sequential Promise chain
UxMotion.cancel()             // hard stop + clear queue
UxMotion.boot()               // play embedded application/ux-motion+json scripts
UxMotion.version              // "1.2.0"
```

### Must match reference player

For any plan **without** bind/scroll side effects:

- Order of animation **starts** for each (target, role) must match `interpret`.
- Order of **ends** must match.
- Absolute millisecond equality is **not** required under CPU contention.

### WAAPI path

- Keyframes from recipe `from` / `to` via transform + opacity + filter + offsetDistance.
- On finish: `commitStyles()` then `cancel()` to freeze computed style.
- Spring recipes: duration estimated from mass/stiffness/damping; easing softened.

### Share (FLIP)

1. `getBoundingClientRect(leave)` and `arrive`.
2. Invert delta (dx, dy, scale) onto arrive as `from`.
3. Animate arrive to identity.
4. Hide leave after finish.

### Bind

- Sets `data-uxm-bind` and listens to scroll when `input==="scroll"`.
- Writes `data-uxm-progress`.
- Still plays child fully on one-shot `play()`; continuous scrub is host-driven via progress attribute.

### Score / cue

- `phase==="hold"`: after child plays, store id in `scores` Map; emit `ux-motion:score-hold`.
- `cue`: delete score; emit `ux-motion:score-resolve`; play optional child.

### DOM events

| Event | detail |
|---|---|
| `ux-motion:start` | `{ id, complete }` |
| `ux-motion:complete` | `{ id, action }` |
| `ux-motion:interrupt` | `{ id }` |
| `ux-motion:score-hold` | `{ id }` |
| `ux-motion:score-resolve` | `{ id }` |

### Classic ops in the same player

`morph`, `remove`, `set_attr`, `set_text` are applied for `send.update` Results and mixed payloads. `set_attr` / `remove` apply to **all** `querySelectorAll` matches.

### Reduced motion

Re-read `matchMedia('(prefers-reduced-motion: reduce)')` on each play (not only at script load).

### View engine

If `plan.engine === "view"` and `document.startViewTransition` exists and motion is not reduced, wrap the run in a View Transition. On failure, fall back to presence.

## What is not contracted

- Exact spring settling time across browsers
- Paint performance
- Layout thrashing under pathological selectors
- Security of `html` injection (trusted server content only)
