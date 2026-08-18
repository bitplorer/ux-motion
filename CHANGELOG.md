# Changelog

All notable changes to **ux_motion** are documented here.

Versioning follows [Semantic Versioning](https://semver.org/) for the **library API** (`API_VERSION` / `__version__`).  
The **plan IR** uses a separate major (`IR_VERSION` / plan field `v`). See `docs/13-VERSIONING.md`.

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
