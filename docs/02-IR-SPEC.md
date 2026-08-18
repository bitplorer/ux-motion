# Intermediate Representation (IR) Specification — v1

This is the **wire format**. Anything that validates through `validate_plan` and serializes with `dumps` is legal IR. Receivers **must ignore unknown fields**.

## Root: Plan

```json
{
  "v": "1",
  "kind": "plan",
  "id": "string-non-empty",
  "interrupt": "replace | queue | ignore",
  "reduced": "skip | simplify | honor | swap",
  "engine": "presence | view | spring",
  "complete": "optional-action-name",
  "reduce_tree": { "...node..." },
  "root": { "...node..." }
}
```

| Field | Required | Default | Rules |
|---|---|---|---|
| `v` | yes (defaulted to `"1"` if missing) | `"1"` | Must equal `"1"` or `PlanError` |
| `kind` | yes (defaulted) | `"plan"` | Must be `"plan"` at root |
| `id` | yes | `"plan"` if key absent; **empty string rejected** | Non-empty after strip |
| `interrupt` | no | `"replace"` | Enum above |
| `reduced` | no | `"simplify"` | Enum above; `swap` requires `reduce_tree` to be useful |
| `engine` | no | `"presence"` | Enum above |
| `complete` | no | — | Must be string if present (action name for `ux-motion:complete`) |
| `reduce_tree` | no | — | A node; used when `reduced=="swap"` and user prefers reduced motion |
| `root` | **yes** | — | Any valid node |

## Node kinds

Every node has `"kind": "<one of below>"`.

### `track`

Single target animation.

```json
{
  "kind": "track",
  "target": "#selector",
  "role": "exit | enter | stay | layout",
  "after": "keep | remove | hide",
  "recipe": { "...recipe..." },
  "html": "<optional server HTML for enter>",
  "name": "optional label"
}
```

| Field | Rules |
|---|---|
| `target` | Required non-empty string (CSS selector) |
| `role` | Default `"enter"`. `layout` is treated as **stay** in scheduling until a future additive measurement field exists; use `share` for FLIP |
| `after` | Default `"remove"` if role is exit, else `"keep"` |
| `recipe` | Required |
| `html` | Optional string. On enter, player injects into the host target |
| `name` | Optional |

### `stagger`

Same recipe applied to all matches of a selector, with increasing delay.

```json
{
  "kind": "stagger",
  "selector": ".card",
  "role": "enter | exit | …",
  "gap_ms": 40,
  "recipe": { },
  "after": "keep"
}
```

Reference player expands to N synthetic targets `selector[0]…selector[N-1]` using `counts[selector]` (default 3 in interpret if not provided).

### `share`

Shared-element continuity. Client measures `leave` and `arrive`.

```json
{
  "kind": "share",
  "id": "hero",
  "leave": "#grid-img",
  "arrive": "#pdp-img",
  "recipe": { "name": "share", "duration": 320, ... }
}
```

| Field | Rules |
|---|---|
| `id` | Required — logical identity name |
| `leave` | Required selector (outgoing visual) |
| `arrive` | Required selector (incoming visual) |
| `recipe` | Optional; default duration 320, enter easing |

`as_update` projects to: mark arrive present + share id; mark leave not present.

### `bind`

Wraps a child node as a progress tape.

```json
{
  "kind": "bind",
  "input": "scroll | drag | progress",
  "target": "#article",
  "until": "optional-token",
  "axis": "x | y | both",
  "child": { "...node..." }
}
```

| Field | Rules |
|---|---|
| `input` | Required enum |
| `target` | Required — element that owns the input (scroll container, drag handle) |
| `child` | Required — the subtree whose schedule is the tape |
| `until` | Optional host-defined end condition token (e.g. `"dismiss"`) |
| `axis` | Optional for drag |

### `score`

Multi-hop presence container.

```json
{
  "kind": "score",
  "id": "checkout",
  "phase": "now | hold | resolve",
  "child": { "...node..." }
}
```

| `phase` | Meaning |
|---|---|
| `now` | Play child normally |
| `hold` | Play child; client retains exiting nodes under this score id until cue |
| `resolve` | Play child in context of resolving (rarely authored directly; prefer `cue`) |

### `cue`

Resolves a held score; optional child plays as the arrival.

```json
{
  "kind": "cue",
  "score": "checkout",
  "child": { "...optional node..." }
}
```

### `group`

Named bag of tracks with a mode.

```json
{
  "kind": "group",
  "name": "main",
  "mode": "wait | sequence | parallel",
  "tracks": [ /* nodes */ ]
}
```

Empty `tracks` is allowed by IR but authors should not emit empty groups (`Scene.named` skips flush if pending empty).

### `phase`

Unordered/ordered bag of children (root of most scenes).

```json
{
  "kind": "phase",
  "mode": "wait | sequence | parallel",
  "stagger_ms": 0,
  "children": [ /* non-empty list of nodes */ ]
}
```

`children` must be non-empty or `PlanError`.

## Recipe object

```json
{
  "name": "fade.enter",
  "from": { "opacity": 0, "x": 0, "y": 16, "scale": 1, "rotate": 0, "blur": 0, "offset": 0 },
  "to":   { "opacity": 1, "x": 0, "y": 0,  "scale": 1, "rotate": 0, "blur": 0, "offset": 1 },
  "duration": 280,
  "delay": 0,
  "easing": "cubic-bezier(0.16, 1, 0.3, 1)",
  "fill": "both",
  "spring": { "mass": 1.0, "stiffness": 280, "damping": 24 },
  "path": { "d": "M0,0 C…", "rotate": "auto" },
  "engine": "spring"
}
```

| Field | Rules |
|---|---|
| `name` | Required string |
| `from` / `to` | Optional objects; only known props kept: opacity, x, y, scale, rotate, blur, offset |
| Numeric props | Must be int/float, **not** bool |
| `duration` | 0..120000 inclusive; default 240 |
| `delay` | ≥ 0; default 0 |
| `easing` | Non-empty string (CSS easing) |
| `fill` | `none\|forwards\|backwards\|both` |
| `spring` | Optional; implies physics path |
| `path` | Optional; `d` required string (SVG path) |
| `offset` in from/to | 0..1 progress along path |

## Validation invariants

1. Idempotent: `validate_plan(validate_plan(p)) == validate_plan(p)` for valid p.
2. Unknown top-level and node fields are **stripped** (not preserved).
3. Invalid enum / type / empty id → `PlanError` (subclass of `ValueError`).
4. `loads(invalid_json)` → `PlanError`.

## Extending IR (for future maintainers)

Allowed without bumping `v`:

- New optional fields on existing nodes (receivers ignore if unknown).
- New optional recipe props (player ignores if unknown).
- New kind **only if** old players can safely no-op unknown kinds at the node level (current JS player no-ops unknown kinds via `playNode` fall-through). Prefer documenting that old players skip unknown kinds.

Not allowed without `v: "2"`:

- Changing meaning of an existing field.
- Making a previously optional field required in a way that rejects old documents.
- Reusing a key for a different type.
