# TELOS tip 67ff3f0 — feature inventory / clarity / IR consumption

> **PLAN-ONLY.** Projection, not law. Law stays [AGENTS.md](../../AGENTS.md),
> [14-CHANNEL-COMPOSITOR.md](../14-CHANNEL-COMPOSITOR.md), and
> [06-DESIGN-DECISIONS.md](../06-DESIGN-DECISIONS.md). Public names stay
> `ux_motion/__init__.py` `__all__`. Numbered `docs/00`–`14` stay.
>
> Phase 0–1 cartograph only. No product code. No fashion restyle.
> No folder taxonomy overlay. No IR `v` bump. No sixth product.
> Channel never learns `transition.*`. `MotionChannel` KEEP.
>
> **Verified 2026-09-12** vs motion `origin/main` `67ff3f0`
> (`docs: expand public-API snippet cookbook`) — pin == tip —
> and live sister tips fetched the same hour.

This page is a **new tip map** for ux-motion. It does not reopen
compose plans #73 / #76 / #77 / #80 / #84 or fashion #67.

---

## 0. Status one-screen

| Layer | Fresh `origin/main` | Motion relation |
|-------|---------------------|-----------------|
| **ux-motion** | `67ff3f0c4912b70b7056f8226a6f226b6fe93f60` | **this tip** (compose `MOTION_VCS_PIN` == tip) |
| **ux-compose** | `fb7a12557146e88266ec5fa6d437f2d3104489e5` | consumer (#84 TELOS map + #83 C2 USE) |
| **ux-channel** | `d0412c62b5180f69e76d16c913809f6c34dee269` | **does not import motion**; Soft 1–4 shipped |
| **ux-behavior** | `793f120e3b1388925772cd069b070d7918b78baa` | XOR fold (`wire/compose.py`); pin == tip |
| **ux-dom** | `d107209` (product pin `2e894cd`) | soft peer (Document + `__render__`) |

**Already landed (do not re-do):**

| Cut | SHA / PR | What |
|-----|----------|------|
| Phase 1 onboarding | #3 | START_HERE, AGENTS, CONTRIBUTING, INDEX |
| Phase 1.1 / 1.2 | #4 #5 | INDEX on overview; gates, brand, hard-cuts |
| Phase 2 Diátaxis | #6 | folder slots; numbered `00`–`14` KEEP |
| Community / cookbook | `6736054` `d0646c5` `67ff3f0` | health files; SNIPPETS |
| Compose pin | compose Makefile / `scaffold.py` | `MOTION_VCS_PIN = 67ff3f0` |

**Soft queue after this inventory: empty.** No dual-door, fail-open,
claimed-false, or unused/dead gap remains that is one concern,
fail-closed, and not a fashion restyle or public-surface delete.

---

## 1. TELOS + ponytail

A layer's **telos** is the end it exists to serve. Callers **USE** that
end. Re-implementing it elsewhere is bloat even when the clone is thin.

| Layer | Telos (owns) | Must not own |
|-------|--------------|--------------|
| **ux-motion** (this repo) | Presence / transition plans as data (IR v1); recipes; Scene; `send.*`; JS/Python players; `Motion` / `MotionChannel` contributions | `@action`, MorphState, Document construction, Cap mint, product CLI |
| **ux-channel** | Intent → Cap → Result; wire; Cap Host; `mount_channel` | HTML trees, CSS, `transition.*` as immortal ops |
| **ux-behavior** | Product meaning → verified `list[Op]`; XOR fold | Raw HTML, wire codecs, motion IR kinds |
| **ux-dom** | Tree → HTML, `Document`, package static | Intent / Cap, MorphState, motion IR |
| **ux-compose** | Author composition + `uxcompose` | Re-implementing any specialist |

**Ponytail** (shrink only in this order — never reverse):

1. **YAGNI** — delete the unused plane if no locked L depends on it.
2. **Reuse the owner** — call the specialist (compose/behavior USE motion IR).
3. **stdlib** — JSON / HTML escape only when the owner has no public API yet.
4. **Minimum local** — smallest adapter (`MotionChannel` hook, compose `_normalize_plan_ops`).

Organize by **capability / happy path**, not by feature folders. One
taught path per job.

**Intent Vector** (required on every DO Soft; none in this queue):

| Field | Meaning |
|-------|---------|
| **Intent** | One capability end (the telos being served) |
| **Vector** | Owner library → compose/channel USE site (`path:line`) |
| **Concern** | One Soft; prefer reuse-owner over rename |
| **Not** | Folder move, public rename, encyclopedia, sixth product |

---

## 2. Feature inventory (this tip)

API **1.3.0** · IR **`v: "1"`** · Player JS **`UxMotion.version` 1.3.0**.
Zero hard deps. `requires-python >= 3.14`. Public surface is 78 names
on `ux_motion/__init__.py` `__all__`.

### 2.1 Capabilities (one taught path each)

| # | Happy path | Owner door | Also exists | Verdict |
|---|------------|------------|-------------|---------|
| M1 | Author a scene | `scene(id).exit/enter/stay` → `.play()` | `Motion.scene`; functional `track` + `.also` | **KEEP** disclosure |
| M2 | Wire Result | `send.play` / `Scene.play` | `play()` ops-only; `Motion.play` | **KEEP** one Result shape |
| M3 | DOM-only clients | `send.update` / `Scene.update` → `as_update` | `also_update=True` embeds `meta.update` | **KEEP** host chooses |
| M4 | Invert / stop | `send.rewind` / `send.cancel` | `rewind_plan`; `Scene.cancel_ops` | **KEEP** |
| M5 | Recipe families | `fade/rise/slide/scale/blur` `.enter/.exit` | `none` `snap` `along` `springy` | **KEEP** names do what they say |
| M6 | Tokens | `tokens.ms/ease/dist/spring_params` | `Tokens` class | **KEEP** |
| M7 | Tree → Scene (BUILD) | `appear` / `swap` / `leave` | family-as-HOF `rise(tree)` | **KEEP** HOF layer |
| M8 | Selector choreography | `page` / `modal` / `toast` / `list_stagger` / `shared_page` | HOF `sheet` / `notice` / `staggered` | leftover pair — **KEEP** (different return: plan vs Scene) |
| M9 | Multi-hop | `scene.as_score` + `cue` | `hop.leave/arrive`; `multi_hop_*` | leftover pair — **KEEP** |
| M10 | FLIP / scrub / groups | `share` / `bind_to` / `named` / `wait\|sequence\|parallel` | functional `share` `bind` `group` | **KEEP** |
| M11 | Inspect | `explain` `interpret` `frames` `span_ms` | `schema` | **KEEP** schedule contract |
| M12 | Wire freeze | `dumps` / `loads` / `freeze_plan` / `Scene.__render__` | `as_html` ≡ `render_markup` | **KEEP** alias |
| M13 | Player on Document | `document.use(Motion())` | `static/` URL copy of the same JS | **KEEP** serve modes |
| M14 | Play after Channel morph | `document.use(Motion(), MotionChannel())` | Host `UxMotion.applyOps` if no Channel | **KEEP** council D16 |
| M15 | XOR on one Result | **ux-behavior** `wire/compose.py` `_reject_overlap` | compose `update_with` (no `html=` on plan) | **KEEP** owner is behavior |

### 2.2 IR kinds (v1 additive)

`plan` · `phase` · `group` · `track` · `stagger` · `share` · `bind` ·
`score` · `cue`.

Modes `parallel|sequence|wait`. Roles `exit|enter|stay|layout`.
After `keep|remove|hide`. Engines `presence|view|spring`.
Bind inputs `scroll|drag|progress`. Ops `transition.play|cancel|rewind`.

Unknown fields ignored. Keys never reused. Breaking receivers requires
a new plan `v`.

### 2.3 Modules (no new ones this pass)

Frozen layout in [00-OVERVIEW.md](../00-OVERVIEW.md). Private
`ux_motion._*` is not a product import path. Tests may touch internals.

---

## 3. How compose / channel consume motion IR

Motion **does not** import `ux_channel` or `ux_compose`. Channel
**does not** import motion. Compose **USE**s the public facade and
leaves XOR to behavior.

### 3.1 Channel @ `d0412c6` — zero consumption

Tree search of `ux-channel` `origin/main`: **no** `ux_motion`,
**no** `transition.play`, **no** `MotionChannel`.

`applyOp` never learns `transition.*`. That is the telos, not a gap.

The only Channel-shaped door is the **contribution hook** this package
owns:

```text
document.use(Motion(), MotionChannel())
  beforeApply  peel transition.* → result._uxMotion
  apply        Channel idiomorph wins the slot
  afterApply   UxMotion.applyOps(stashed) if the player is present
```

Evidence: `ux_motion/_channel.py` (contribution; `ImportError` → empty
scripts when ux-dom is absent). `ux_motion/scripts/ux-motion-channel.js`
(`isMotion` prefix `transition.`; play gated on `global.UxMotion`).
`static/` copy is byte-identical.

### 3.2 Behavior @ `793f120` — XOR fold, opaque plan

| Site | What | Verdict |
|------|------|---------|
| `ux_behavior/wire/compose.py` | `compose()` flattens Scene via `.play()` / `.ops()`; `_reject_overlap` walks `plan` for `html` + `target` | **OWNER** of XOR. Fail-closed `Conflict` |
| `ux_behavior/wire/result.py` | Same law on live Result | **KEEP** |
| tests `test_compose` / `test_result` / `test_live_channel` | `transition.play` as opaque ops | not a clone |

Motion docs that cite `ux_behavior.wire.compose` (historical
`ux_app.adapter.compose`) are **true**. Not claimed-false.

### 3.3 Compose @ `fb7a125` — USE sites

Line numbers are compose tip `fb7a125` unless noted.

| # | Happy path | Compose USE | Re-implement risk | Verdict |
|---|------------|-------------|-------------------|---------|
| C-M1 | Attach player + hook | `wire/boot.py:160-176` `attach_motion` → `from ux_motion import Motion, MotionChannel` (Isolation: only here); `App.use_motion` `app.py:145-160` | Host `glue.js` (banned) | **KEEP** USE both |
| C-M2 | Domain stamp | `App._register_motion_stamp` `app.py:211-218` `behavior.domain("motion", "1", pairs=transition.{play,cancel,rewind})` | `except Exception` swallow | compose leftover — **not** a motion Soft |
| C-M3 | Scene → Op | `helpers._normalize_plan_ops` `:351-383` wraps Scene/plan as `transition.play`; probes `.plan()` / `.to_plan()` | `except Exception: pass` on probe | compose parked (compose TELOS §4.5). Scene has `plan()`, not `to_plan` |
| C-M4 | Morph-then-Play | `update_with` `:386-431` morph first, then C-M3; docstring XOR: never injects `html=` onto the plan | `morph_play` `:434-439` thinner twin | compose leftover dual — **KEEP** (taught: `update_with`) |
| C-M5 | Author helpers | `author.py:14` `scene, rise, fade, slide, tokens`; `optional_plan/fade/slide` `:23-37` | root `__init__.py:40` re-exports same four | compose author surface. **KEEP** |
| C-M6 | Kit overlay enter | `kit/overlay.py:104-129` `open_plan()` selectors-only (no `html=`) | `except Exception: return None` | compose leftover optional. **KEEP** |
| C-M7 | Wire project | `wire/caps.py:179-180` `name=="play" or ns=="transition"` → `{op: transition.play, plan}` | Channel learning the op | projection only. **KEEP** |
| C-M8 | Doctor / probe | `dx/probe.py` `ux_motion` presence; `doctor.py` specialist table | merge doctors | **KEEP** homonym |

**OWNER-WRONG live re-impl of motion IR in compose/channel: none.**
Compose does not compile plans, freeze html, or interpret schedules.
It wraps a Scene/plan as a Channel-shaped op and attaches the
contribution pair.

Taught product path (one):

```text
@action → update_with(self, scene("x").enter("#face", rise.enter()))
         morph(T) first, plan has no html= on T
         XOR owned by behavior.compose if someone also pass html=
Document.use(Motion(), MotionChannel())   # attach_motion
```

Compose consumes a **narrow** façade: `scene`, `fade`, `rise`, `slide`,
`tokens`, `Motion`, `MotionChannel`. It does not call HOF/patterns/
`share`/`bind`/`score`/`stamp`. Unused-by-compose ≠ dead-in-motion.

---

## 4. Clarity / denoise / maturity

Docs Phase 1–2 already shipped (#3–#6). Numbered `00`–`14` + INDEX
routing + START_HERE 5-minute path + SNIPPETS cookbook. **Do not
restyle.** Residual noise is leftover teaching, not a Soft.

| Lens | Score (1–5) | Residual (KEEP, not Soft) |
|------|-------------|---------------------------|
| Navigability (2-click) | 5 | START_HERE → INDEX → 00 / 03 / 14 |
| Diátaxis purity | 4 | `00-OVERVIEW` remains mixed overview; INDEX assigns explanation |
| Ownership vs code | 5 | `__all__` matches 03; Channel has zero motion refs |
| Information preservation | 5 | numbered set ADAPT/KEEP |
| Professional maturity | 5 | 1.3.0 / IR v1 / player aligned; MIT; unittest gate |
| Denoise | 4 | leftover tarball cwd in `09-TESTING.md`; leftover `stamp`/`region`/`Presence`; leftover HOF↔pattern names |

Phase 2 folder slots already point at 00–14. `docs/plans/` is
**projection only** (this file). INDEX stays the map. Do not add a
second competing map.

---

## 5. Especially checked

Soft DO only for **dual door**, **fail-open**, **claimed-false**,
**unused/dead**. Fashion restyle is not a Soft.

### 5.1 Dual doors

| Pair | Same job? | Close how | Verdict |
|------|-----------|-----------|---------|
| `Scene.play` / `send.play` / `play()` / `Motion.play` | Yes — one Result | Disclosure. `play()` is ops-only | **KEEP** |
| Functional `track`/`wait` vs Scene methods | No — nodes vs builder | Compose with `.also` | **KEEP** |
| HOF `sheet`/`notice`/`staggered`/`hop.*` vs patterns `modal`/`toast`/`list_stagger`/`multi_hop_*` | Overlap | Different contract: trees→Scene vs selectors→plan | leftover-taught **KEEP**. Merging is public rename |
| `as_html` vs `render_markup` | Alias | Documented leftover name | **KEEP** |
| `scripts/*.js` vs `static/*.js` | Byte-identical | `package_mount` vs standalone URL | **KEEP** |
| compose `update_with` vs `morph_play` vs `enter(html=)` | Morph-then-Play vs inject | Taught: `update_with`; XOR at behavior | compose leftover **KEEP** |
| compose root re-export `scene/fade/rise/slide` | Author convenience | Isolation: product imports compose | not a motion Soft |

No second taught path that **fails closed differently** from the first.

### 5.2 Fail-open

| Site | Evidence | Why not a cut |
|------|----------|---------------|
| Channel ignores `transition.*` | zero refs @ `d0412c6` | Antifragile (council §5). Safe no-op |
| Hook no-ops if `UxMotion` missing | `ux-motion-channel.js` afterApply gate | Taught pair is `Motion()` + `MotionChannel()`. Compose `attach_motion` always returns both. Reopening the hook needs council §6 |
| `MotionChannel.document_head` without ux-dom | `ImportError` → `()` | Optional peer. **KEEP** |
| `_render._stamp_if_nonce` `except Exception` | CSP stamp degrade | Optional ux-dom. **KEEP** |
| `as_update` stay/layout skip | `_ops.py` walk; empty → `noop` | D8 is “no silent **empty** list”. CONTRACT wording is stronger; leftover, not fail-closed |
| compose `_normalize_plan_ops` `except Exception` | `helpers.py:375-379` | Parked on compose TELOS §4.5 |
| compose `overlay.open_plan` `except Exception: return None` | `kit/overlay.py:106-109` | compose leftover optional. Hard-dep now exists |
| Unknown IR fields ignored | IR law | **KEEP** |

Do not open a “remove all except Exception” Soft. That is fashion.

### 5.3 Claimed-false

| Claim | Evidence | Verdict |
|-------|----------|---------|
| XOR enforced at `ux_behavior.wire.compose` | `compose.py:90-105` `Conflict` | **true** |
| Channel never learns `transition.*` | channel tree empty | **true** |
| Player version == API 1.3.0 | `_contract.py`, `__init__`, JS | **true** |
| Presence per `data-uxm-id` | player writes `data-uxm-present/role/bind/progress`; **never reads** `data-uxm-id` | leftover helper speech. Encyclopedia, not a product lie |
| `09-TESTING.md` `cd ux_motion-1.0.0-complete` | ghost tarball path; CONTRIBUTING/AGENTS cwd is repo root | leftover how-to. Encyclopedia-only — **fails** Pattern/Clarity Soft gate |
| `as_update never drops a track silently` | stay/layout emit nothing if another op exists | D8 = empty→`noop`. Wording drift. **KEEP** |

### 5.4 Unused / dead

| Symbol / file | Callers | Verdict |
|---------------|---------|---------|
| `stamp` / `region` / `Presence` | none in tests, examples, compose, or player | leftover public HTML helpers (layer must not own DOM construction). Deleting `__all__` is E14. **KEEP** leftover |
| `HOFS` / `PATTERNS` catalogs | members used; dicts unused in tests | discovery tables. **KEEP** |
| `to_plan` | compose probe only; Scene has `plan()` | compose leftover, not motion dead code |
| `cli` / `serve` / `create_app` | resilience test asserts **absent** | **DEAD** doors stay gone |
| `scripts/` vs `static/` JS | both served; diff empty | not dead |

Root `__all__` is the lock. Do not invent a “delete unused exports”
Soft.

---

## 6. Ranked DO / KEEP / DEAD / DO NOT

### DO (Phase 2 — separate PRs, one concern + Intent Vector)

**None.** Soft queue is empty.

Rejected as DO (so the next agent does not re-open them):

| Candidate | Why not |
|-----------|---------|
| Delete `stamp` / `region` / `Presence` | Public `__all__` break. Leftover, not fail-closed |
| Merge HOF ↔ patterns (`sheet`/`modal`, `notice`/`toast`, `hop`/`multi_hop`) | Public rename. Different return types |
| Fix `09-TESTING.md` tarball cwd | Encyclopedia-only. CONTRIBUTING already has the gate |
| Tighten CONTRACT “never drops a track” to emit stay ops | Fashion vs D8 |
| Reopen MotionChannel if player absent | Council §6. Taught pair + compose `attach_motion` |
| Teach Channel `transition.*` | Immortal op table. **Never** |
| Pin / consume compose `fb7a125` from this repo | Motion has zero hard deps. YAGNI |
| Docs-first INDEX / Diátaxis restyle | Phase 2 already landed. Fashion |
| Invent `to_plan()` so compose probe hits | Compose leftover. Do not grow a second Scene door |

### KEEP

Scene fluent + functional nodes · `send` / `Scene.play` · HOF layer ·
pattern layer · `as_html` alias · dual JS copies · `Motion` +
`MotionChannel` pair · XOR at behavior · Channel ignorance of
`transition.*` · leftover `stamp`/`region`/`Presence` · compose
`update_with` · compose `_normalize_plan_ops` probe · numbered
`docs/00`–`14` · Phase 2 folder slots · IR v1 additive ·
`requires-python >= 3.14` matching compose / ux-dom.

### DEAD (doors gone, teaching stays)

Product CLI · `ux_motion.serve` · `create_app` · Host `glue.js` ·
Channel-owned `transition.*` · `as_html` at `enter()` (moved to wire).

### DO NOT (kill list)

- Fashion restyle of numbered docs, INDEX, or folder taxonomy.
- Teaching Channel `transition.*`.
- Sixth product (`ux-app`, `ux_channel_ux_motion` repo for 40 lines of JS).
- Rename contribution to Glue / Bridge / Adapter.
- Play motion *before* Channel morph.
- Change player `morph` back to `innerHTML`.
- Reuse IR keys; bump plan `v` for this map.
- Import private `ux_motion._*` from product code.
- Pixel-identical physics as a contract (schedule **order** is the contract).
- Merge HOF and patterns.
- Gut `__all__` “unused” names.
- Reopen compose #73 / #76 / #77 / #80 / #84 / #67.
- Invent lockfiles / load / chaos harnesses for vanity.

---

## 7. Soft order

| # | Owner repo | Status | Next |
|---|------------|--------|------|
| Docs Phase 1–2 | **ux-motion** | shipped #3–#6 | none |
| Compose C2 USE + pin | **ux-compose** | shipped #83 / #84 | none |
| Channel Soft 1–4 | **ux-channel** | shipped @ `d0412c6` | none |
| XOR fold | **ux-behavior** | shipped `wire/compose.py` | none |
| **Open Softs** | — | **empty** | stop |

Framework Lock held: same products, native composition styles.
Ponytail: no Soft that only rearranges docs or public names.

---

## 8. Pattern / Clarity gate (any later cut)

A DO row ships only when **both** pass:

| Test | Pass | Fail |
|------|------|------|
| **Pattern** | Matches leftover-teach / fail-closed / prefer-owner | New folder, new public name, new product door, new test *layer* |
| **Clarity** | Names the leftover; one concern; same-commit lock | Encyclopedia-only, or “while we’re here” |

Ponytail on every cut: YAGNI → reuse owner → stdlib → minimum local.

**Stop / revert if:** Channel learns `transition.*` · `MotionChannel`
renamed Glue/Bridge/Adapter · new root `__all__` · plan `v` bumped ·
numbered docs flattened · Isolation (motion imports `ux_channel`).

---

## Appendix. One screen

```text
MOTION @ 67ff3f0 (pin == tip)
  scene().play()     taught author door          KEEP
  send.*             Result shape                KEEP
  HOF vs patterns    leftover pair               KEEP
  Motion+MotionChannel  after Channel morph      KEEP
  XOR                behavior.wire.compose       KEEP
  Channel            zero motion refs            KEEP

COMPOSE USE @ fb7a125
  attach_motion      Motion + MotionChannel      USE
  update_with        morph then transition.play  USE
  author/kit         scene, fade, rise, slide    USE
  _normalize_plan_ops  wrap Scene as op          leftover probe KEEP

SOFT QUEUE                                   EMPTY
DO NOT
  teach Channel transition.* · fashion restyle
  delete leftover __all__ · merge HOF/patterns
  reopen compose plans · sixth product
```
