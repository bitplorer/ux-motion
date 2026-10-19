# Changelog

All notable changes to **ux_motion** are documented here.

Versioning follows [Semantic Versioning](https://semver.org/) for the **library API** (`API_VERSION` / `__version__`).  
The **plan IR** uses a separate major (`IR_VERSION` / plan field `v`). See `docs/13-VERSIONING.md`.

---

## Unreleased

### Fixed — Idiomorph throw keeps a focused host

`injectHtml` caught an Idiomorph failure, `replaceChild`'d the live host,
and did not log or rethrow. A focused input was a new node: focus and the
typed value were gone, and the caller saw a successful morph. If the host
is focused or contains the focused element, the host now stays (value
included) and the error is written with `console.error`. An unfocused host
still falls back to `replaceChild` after that log. Rethrowing would abort
`applyOp` before the caller can observe the preserved node.

Host-owned escaping is unchanged. The compositor doc no longer says this
path never uses raw `innerHTML`: the incoming string is parsed with
`innerHTML`, and the no-element / no-Idiomorph fallbacks assign it too.

### Fixed — explicit duration 0 stays 0

An explicit recipe `duration` of `0` was rewritten to a default. Python
`span_ms` on a share used `duration or 320` (a track already kept 0; 240
is only the recipe default when duration is unset). The web player used
`|| 240` for tracks and `|| 320` for share, so `Element.animate` never
saw 0. Missing duration still defaults to 240 (track / `recipeDuration`)
or 320 (share when the recipe omits it). `0` now stays `0` on both
players (`??` in the web player).

`armEl` still passes `duration || 1` into WAAPI. A scrub tape pauses the
effect and seeks `currentTime`; a 0 ms effect is already finished and is
not seekable. That 1 ms floor is only the WAAPI timing option. Logical
duration from `recipeDuration` is unchanged, and `animateEl` (play) passes
the real duration, including 0.

### Removed — dead imports (no API change)

- Unused imports in `ux_motion/_api.py` (`rewind_plan`), `ux_motion/_freeze.py`
  (five `KIND_*` constants) and `ux_motion/_patterns.py` (`Mapping`, `cue`,
  `score`), plus unused imports in `tests/` and `examples/minimal.py`.
  The public facade (`ux_motion.__all__`) is unchanged.
- `tests/test_no_unused_imports.py` (stdlib only) keeps them gone.
- Version stays 1.3.0: the library, the player JS and `CONTRACT` move in
  lockstep (docs/13-VERSIONING.md), and nothing in the API or player changed.

### Docs Soft — Soft 1–3 teaching (2026-09-13)

- Human-readable Soft 1 (`scrub` / `UxMotion.scrub`), Soft 2 (`morph_d` /
  `morph.d`), Soft 3 (`partition_wait` / `wait_clocks`) under Diátaxis:
  README front door, START_HERE §§3b–3d, OWNERSHIP leftover teaching,
  SNIPPETS how-to, numbered 00 / 03 / 05 / 07 / 09 / 10.
- Honest Soft LOCK: hover/tap/press/pan/drag and Framer `while*` are
  Channel Intent / Behavior `@action`. Not this layer. No gesture Soft.
- Leftover (HOLD): Framer variants dump, drag-as-gesture, motion values /
  React API. Soft 1–3 KEEP. `bind.input === "drag"` remains one-shot play.
- Leftover how-to: `docs/09-TESTING.md` no longer `cd`s a ghost tarball
  path (`ux_motion-1.0.0-complete`).

### Soft 3 — wait completeness (2026-09-13)

- Lock wait orchestration: direct `exits` then `stays` then `enters`;
  `nested` units start at `t0`. Frozen names: bags `exits` / `stays` /
  `enters` / `nested`; clocks `exit_end` / `stay_end` / `enter_t`;
  Python `partition_wait` / `wait_clocks` (`WaitBags` / `WaitClock`);
  JS `partitionWait`. `CONTRACT["wait.bags"]` / `wait.clocks` /
  `partition_wait`. Missing role is enter. `stagger_ms` does not apply
  to wait bags.
- Soft 1 scrub KEEP. Soft 2 `morph.d` KEEP.
- Soft LOCK: no gesture Soft. Hover/tap/press/pan/drag and Framer
  `while*` are Channel Intent / Behavior `@action`. Cap Host not invented.
- **Leftover (HOLD):** Framer variants dump, reorder, motion values /
  React API, drag-as-gesture. Teaching: [OWNERSHIP.md](OWNERSHIP.md).
  `bind.input === "drag"` remains one-shot play.

### Soft 2 — SVG path d morph (2026-09-13)

- Additive recipe field `morph.d.{from,to}` (similar SVG path strings).
  Frozen names: recipe `"morph.d"`; Python `morph_d` / `Recipe.with_morph_d`;
  `CONTRACT["morph.d"]`. `path` stays offset-path (`along`). Keys not reused.
- Player: thin WAAPI `d: path("…")` interpolation plus `setAttribute("d")`
  commit. Soft 1 scrub KEEP (`UxMotion.scrub` / `applyTape`).
- Soft LOCK: no gesture Soft. Gestures are Channel Intent / Behavior
  `@action`. Cap Host not invented.
- Soft 3 wait completeness shipped above. Leftover teaching:
  [OWNERSHIP.md](OWNERSHIP.md). `bind.input === "drag"` remains one-shot.

### Soft 1 — scroll-scrub lock (2026-09-13)

- `bind` IR KEEP (`input` / `target` / `child` / `until` / `axis`). No new keys.
- Player: live WAAPI tape for `bind.input === "scroll"` (rAF-coalesced scroll
  loop drives `currentTime`). `data-uxm-progress` still written.
- Frozen scrub names: Python `scrub(plan, progress)` → `ScrubFrame`;
  JS `UxMotion.scrub(planId, progress)`. `CONTRACT["scrub"]` / `player_exports`.
- Soft LOCK: no gesture Soft. Gestures are Channel Intent / Behavior
  `@action`. Cap Host not invented; channel stays `transition.*`.
- Soft 2 / Soft 3 shipped above. Leftover teaching:
  [OWNERSHIP.md](OWNERSHIP.md). `bind.input === "drag"` remains one-shot.

### Python floor (2026-09-12)

- `requires-python >= 3.14` (matches compose and ux-dom). Classifiers drop 3.10–3.12.

### Completeness (2026-08-19)

- README / OVERVIEW: MIT (not a placeholder), current package layout (HOF + MotionChannel + scripts).
- `pip install ux-motion`; GitHub URLs on the package metadata.
- XOR cite updated to `ux_behavior.wire.compose` (historical `ux_app.adapter.compose`).
- Tests: `static/` JS must equal `ux_motion/scripts/` JS; player version string matches Python.

---

## 1.3.0 — 2026-08-18

Channel compositor as a Document contribution. IR stays `"1"`.

### Library

- `MotionChannel()` — `document.use(Motion(), MotionChannel())`
  injects `ux-motion-channel.js`
- The hook peels `transition.*` on `channel:beforeApply` and plays them
  on `channel:afterApply` so Channel idiomorph wins the slot first
- Player `applyOp("morph")` uses `injectHtml` (Idiomorph when host id
  matches) instead of `innerHTML`
- Not Glue (`ux_channel_ux_dom`), not a Bridge, not an Adapter
- Binding reasons + how to change later:
  [docs/14-CHANNEL-COMPOSITOR.md](docs/14-CHANNEL-COMPOSITOR.md) · D16

---

## 1.2.2 — 2026-08-18

Player: close two `injectHtml` edges after the Idiomorph switch.

- Re-resolve the live host if a tag-name change replaces the node (never animate a detached element)
- Cancel any `fill: both` animation on the target *before* morphing (replaceChild used to drop it by destroying the node)
- `restoreFocus: false` so a morph does not steal an input caret
- Morph errors fall back to `replaceChild`

---

## 1.2.1 — 2026-08-18

Player: morph matching hosts instead of replacing them.

### Library

- `injectHtml` uses `Idiomorph.morph` when the incoming root and the live host share an `id`
- Matching descendants (especially `img-{sku}`) keep their decoded bitmaps across `appear` / `swap` / `enter(..., html=)`
- Falls back to `replaceChild` when Idiomorph is not on the page
- IR stays `"1"`

---

## 1.2.0 — 2026-08-18

Drop-in higher-order functions. Trees in, Scene out.

### Library

- `appear(tree)`, `swap(host, tree)`, `leave(target)`, `sheet(overlay, panel)`, `notice(tree)`, `staggered(host, children)`, `hop.leave` / `hop.arrive`
- Recipe families are callable: `rise(tree)` → Scene, `rise(ms=180)` → Recipe
- `@motion` decorator wraps a view function as a Scene (`fn.view` is the original)
- All HOFs return a live `Scene` (BUILD). Serialize still happens at `.play()` / `dumps` / `__render__`
- `css_target` infers `#id` from a ux-dom tree
- Existing `page` / `modal` / `toast` patterns unchanged (still return plans)

---

## 1.1.0 — 2026-08-18


ux-dom render-model integration. Trees stay trees until official serialize.

### Library

- `enter(..., html=tree)` / `track(..., html=tree)` keep ux-dom Components through BUILD
- `freeze_plan` / `render_markup` serialize at the wire only (`stamp_tree` + `__render__`)
- `dumps`, `send.play` / `update` / `rewind`, and `Scene.__render__` freeze automatically
- `Scene` implements `__render__` / `__html__` / `__str__` / `__iter__` so HTMLResponse, Channel, and `div(scene)` emit a `<script type="application/ux-motion+json">` carrying the full plan
- `document.use(Motion())` injects the player the same way `XElement` does (`/ux-pkg/ux-motion/static/ux-motion-player.js`)
- Player boots embedded plan scripts on `DOMContentLoaded` (`UxMotion.boot`)
- Package data includes `ux_motion/scripts/ux-motion-player.js` for `SafeStaticFile`

### Docs / tests

- Architecture and wire protocol document the two-phase model
- `tests/test_render_model.py` covers fake trees, real ux-dom trees, and Document runtime

### Compatibility

- IR stays `"1"`. Wire `html` is still a string. Authoring may now hold a renderable until serialize.
- `as_html` is an alias of `render_markup` (no longer called at `enter()`)

---

## 1.0.0 — 2026-08-18

First public release of **ux_motion** as a complete library.

### Library

- Python facade: `scene`, recipes, `send.play` / `send.update` / `send.rewind` / `send.cancel`
- IR v1: plan, phase, group, track, stagger, share, bind, score, cue
- Composition modes: `wait`, `sequence`, `parallel` with nested-group independence
- Recipes: fade, rise, slide, scale, blur, none, snap, along(path), springy
- Design tokens: duration, easing, distance, spring presets
- Patterns: page, modal, toast, list_stagger, shared_page, multi_hop_leave/arrive
- Reference player: `interpret`, `explain`, `frames`, `span_ms`
- Classic projection: `as_update` never drops tracks
- JSON Schema export: `schema()`
- Single version source: `ux_motion/_version.py`
- Vanilla JS player: `static/ux-motion-player.js` (`UxMotion.version == 1.0.0`)

### Docs

- Overview, architecture, IR spec, API reference, composition semantics
- Player contract, design decisions, enhancements, wire protocol
- Testing, examples, glossary, Mermaid diagram set, versioning policy

### Compatibility

- Plan wire field `v` must be `"1"`
- Unknown IR fields are ignored by validators and should be ignored by receivers
