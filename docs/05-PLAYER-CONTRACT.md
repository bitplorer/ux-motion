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
UxMotion.cancel()             // hard stop + clear queue + release bind tapes
UxMotion.boot()               // play embedded application/ux-motion+json scripts
UxMotion.scrub(planId, p)     // Soft 1: seek a bound tape; progress 0..1
UxMotion.version              // "1.3.0"
```

### Must match reference player

For any plan **without** bind/scroll side effects:

- Order of animation **starts** for each (target, role) must match `interpret`.
- Order of **ends** must match.
- Absolute millisecond equality is **not** required under CPU contention.

### WAAPI path

- Keyframes from recipe `from` / `to` via transform + opacity + filter + offsetDistance.
- Soft 2: recipe `morph.d` adds CSS `d: path("…")` on the same animation
  (similar path strings). On finish (or if WAAPI rejects `d`), `setAttribute("d", to)`.
- `path.d` remains offset-path (`offsetPath` / `offsetRotate`).
- On finish: `commitStyles()` then `cancel()` to freeze computed style.
- Spring recipes: duration estimated from mass/stiffness/damping; easing softened.

### Share (FLIP)

1. `getBoundingClientRect(leave)` and `arrive`.
2. Invert delta (dx, dy, scale) onto arrive as `from`.
3. Animate arrive to identity.
4. Hide leave after finish.

### Bind

- Sets `data-uxm-bind` on the host (`target`, else `documentElement`).
- `input==="scroll"`: arms paused WAAPI for the child tape; rAF-coalesced
  scroll loop measures progress (overflow host or viewport-crossing) and
  seeks `animation.currentTime`. Writes `data-uxm-progress`.
- `input==="progress"`: arms the same tape at 0; host seeks via `UxMotion.scrub`.
- `input==="drag"`: leftover one-shot child play (no pointer listeners).
- Frozen seek: `UxMotion.scrub(planId, progress)` and Python `scrub(plan, p)`.
- Soft LOCK: no `whileHover` / `whileTap` / `whileFocus` / `whileDrag`.

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
