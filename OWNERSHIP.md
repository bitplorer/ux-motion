# Ownership — ux-motion leftover teaching

> **Diátaxis:** explanation · leftover teaching · **Layer:** ux-motion
> Map: [docs/INDEX.md](docs/INDEX.md). Gate: [README.md](README.md).

This file names **what this layer owns**, **what it must not own**, and the
Soft leftover after Soft 1–3. It is leftover teaching — not a sixth product,
not a gesture library, not a Framer port.

Public names: `ux_motion.__all__`. If this page and code disagree, **code wins**.

---

## Layer cut

| Layer | Owns | Must **not** own |
|-------|------|------------------|
| **ux-dom** | HTML/CSS/JS trees, `Document`, serialize, `uxdom` | Intent, Cap, Result ops, MorphState, motion IR, product CLI |
| **ux-channel** | Intent / Result / Cap / wire / peers / host runtime | HTML trees, CSS, `transition.*` as immortal ops |
| **ux-behavior** | Product behavior, Morph/Ref, `@action`, validation | Raw HTML construction, wire codecs, motion IR |
| **ux-motion** (this repo) | Presence / transition plans as data (IR v1) | Product behavior, DOM construction, gesture listeners |
| **ux-compose** | Author composition + product CLI (`uxcompose`) | Re-implementing any specialist |

Channel never learns `transition.*`. `MotionChannel` peels those ops off the
Result. XOR: `morph(T)` XOR `scene.enter(T, html=…)`.

This package does **not** mint Caps or invent a Cap Host.

---

## Soft 1–3 KEEP (shipped @ `a598bb3`)

Locked from the tree and tests (`tests/test_soft1_scrub.py`,
`tests/test_soft2_path_morph.py`, `tests/test_soft3_wait.py`,
`tests/resilience/test_ownership_isolation.py`). Runnable samples:
[examples/scroll_scrub.py](examples/scroll_scrub.py),
[examples/path_morph.py](examples/path_morph.py),
[examples/wait_complete.py](examples/wait_complete.py).

| Soft | Owns here | Frozen names | Not |
|------|-----------|--------------|-----|
| **1** | Scroll → 0..1 tape | `bind_to("scroll", …)`, `scrub(plan, p)` → `ScrubFrame`, JS `UxMotion.scrub`, `CONTRACT["scrub"]` | Pointer listeners, hover/tap/press/pan/drag Soft |
| **2** | Similar SVG path `d` morph | Recipe `"morph.d"`, `morph_d` / `Recipe.with_morph_d`, `CONTRACT["morph.d"]` | Reusing `path` (that is `along` / offset-path) |
| **3** | Wait bags + clocks | Bags `exits` / `stays` / `enters` / `nested`; clocks `exit_end` / `stay_end` / `enter_t`; `partition_wait` / `wait_clocks`; JS `partitionWait` | Framer AnimatePresence / variants dump |

IR `bind` keys (`input` / `target` / `child` / `until` / `axis`) and
`phase.mode` / `group.mode` `"wait"` are **KEEP**. Additive fields only.

---

## Soft LOCK — gestures are not this layer

Hover, tap, press, pan, drag listeners and Framer `whileHover` / `whileTap` /
`whileFocus` / `whileDrag` / `whileInView` are **not** authored here.

**Where they belong:** Channel **Intent** (the event on the wire) and
Behavior **`@action`** (product behavior). This layer may receive a Plan on
the Result after that Intent is handled. It does not attach pointer
listeners or export those names (`__all__` and the JS player lock this).

`bind.input` enum stays `scroll` | `drag` | `progress` (IR KEEP). Only
`scroll` (and host-driven `progress` via `UxMotion.scrub`) is a live tape.
`drag` remains one-shot child play — leftover IR name, not a gesture Soft.

---

## Leftover (HOLD)

Name the leftover so it is not mistaken for the next Soft:

| Leftover | Status | Owner if it ever ships |
|----------|--------|------------------------|
| Framer variants / `while*` dump | HOLD | Not this layer (see Soft LOCK) |
| Drag bind as a pointer gesture | HOLD | Channel Intent / Behavior `@action` |
| Motion values / React API | HOLD | Out of stack (no React runtime here) |
| Reorder / AnimatePresence dump | HOLD | Wait completeness is already Soft 3 data |

Do **not** start a gesture Soft, a Framer-variants Soft, or a Cap Host in
this repo. Soft 1–3 are closed.

---

## Where to read

| Mode | Doc |
|------|-----|
| Tutorial | [START_HERE.md](START_HERE.md) §§3b–3d |
| How-to | [docs/guides/SNIPPETS.md](docs/guides/SNIPPETS.md) · [docs/07-ENHANCEMENTS.md](docs/07-ENHANCEMENTS.md) |
| Reference | [docs/03-API-REFERENCE.md](docs/03-API-REFERENCE.md) · [docs/02-IR-SPEC.md](docs/02-IR-SPEC.md) · [docs/04-COMPOSITION-SEMANTICS.md](docs/04-COMPOSITION-SEMANTICS.md) · [docs/05-PLAYER-CONTRACT.md](docs/05-PLAYER-CONTRACT.md) |
| Explanation | [docs/00-OVERVIEW.md](docs/00-OVERVIEW.md) · [docs/06-DESIGN-DECISIONS.md](docs/06-DESIGN-DECISIONS.md) D17 |
| History | [CHANGELOG.md](CHANGELOG.md) Unreleased |
