# Council Decision — Channel compositor (`MotionChannel`)

**Date:** 2026-08-18
**Status:** Binding. Supersede only with a new council entry that cites a
reopen condition below.
**Library:** ux-motion **1.3.0** (IR stays `"1"`)
**Question:** Where does “play `transition.*` after Channel idiomorph”
live, and what must it never become?
**Sister record:** [bitplorer/ux-app `docs/STACK_CLEANUP_COUNCIL.md`](https://github.com/bitplorer/ux-app/blob/main/docs/STACK_CLEANUP_COUNCIL.md)
**ADR:** D16 in [06-DESIGN-DECISIONS.md](06-DESIGN-DECISIONS.md)

Read **§6 before you change the hook, the player morph path, or the
name.** That section is the change-assessment checklist.

---

## 1. The problem

A Channel Result may carry both:

- authority morph (`{op: morph, morph: idiomorph, target, html}`)
- motion (`{op: transition.play, plan}`)

Channel `applyOp` does **not** understand `transition.*`. If motion
injects HTML for a target Channel just morphed, identified images
(`id="img-{sku}"`) remount and flash. If the Host ships a file called
`glue.js` to peel those ops, it steals a reserved word: **Glue** is
already `ux_channel_ux_dom`.

## 2. Decision

`MotionChannel` is a **Document contribution** in this package.

```python
document.use(Motion(), MotionChannel())
```

| Piece | Role |
|-------|------|
| `ux_motion.MotionChannel` | `name="ux_motion.channel"`; injects the hook |
| `ux-motion-channel.js` | `channel:beforeApply` peels `transition.*` into `result._uxMotion`; `channel:afterApply` calls `UxMotion.applyOps` |
| Player `applyOp("morph")` | Uses `injectHtml` (Idiomorph when host `id` matches), never raw `innerHTML` |

Motion **does not** import `ux_channel`. Channel **does not** import
motion. Event names (`channel:beforeApply` / `afterApply`) are public
Channel API.

## 3. Why here (not elsewhere)

| Alternative | Why it dies |
|-------------|-------------|
| Teach Channel `transition.*` | Immortal op table learns a droppable peer. Motion cannot be omitted. |
| Host `glue.js` | **Glue** already means `ux_channel_ux_dom`. One intent, one name. |
| Call it a Bridge | Bridge = npm islands. Wrong reserved word. |
| `ux_app.adapter` JS | Adapter is the **Python** import wall. Mixing planes. |
| New `ux_channel_ux_motion` repo | 40 lines of JS is a contribution, not a package. Mint a repo only if a Python interop surface appears. |
| Motion plays *before* Channel morph | Authority loses the slot; images remount. |

Order is the product:

```text
beforeApply  peel transition.*
apply        Channel idiomorph wins the slot (ids reused)
afterApply   UxMotion.applyOps on the stashed list
```

XOR (enforced at Python fold time — historically `ux_app.adapter.compose`,
now `ux_behavior.wire.compose`; not in this hook):

```text
on one Result:  morph(T, tree)  XOR  scene.enter(T, html=tree)
```

The hook cannot see author intent. Compose rejects the clash at
Python fold time. Motion **without** `html` on `T` may share the
target (animate a just-morphed node).

## 4. What this is not

- Not Glue (`ux_channel_ux_dom`).
- Not a Bridge (npm island).
- Not an Adapter (Python import wall).
- Not Host chrome (toast TTL, img `src` pin stay in the Host until
  3+ independent Hosts share the policy).
- Not an IR break. Plan `v` stays `"1"`.

## 5. Antifragile properties

- New HOF → this hook still peels only `transition.*`.
- New Channel op → this hook ignores it.
- Drop `MotionChannel()` → Channel still morphs; motion ops are
  ignored by Channel (safe no-op, no crash).
- Drop Channel → omit `MotionChannel()`; `UxMotion.applyOps` still
  plays embedded plans.
- Player morph via `injectHtml` keeps identified descendants.

## 6. How to change this later

Cite a reopen condition or write a new council entry first.

| You want to… | Legal when | Still illegal |
|---|---|---|
| Teach Channel `transition.*` | Never | Op-table pollution |
| Rename to `glue` / Bridge / Adapter | Never | Reserved words |
| Extract `ux_channel_ux_motion` | Hook grows a **Python** interop surface | Package for 40 lines of JS |
| Move the hook into `ux_app.adapter` | Never | JS in the Python wall |
| Play motion *before* Channel morph | Never (images remount) | Reordering the events |
| Pin `<img src>` inside this hook | 3+ independent Hosts share the policy | One Host’s pantry |
| Change player `morph` back to `innerHTML` | Never | Remount landmine |
| Bump IR `v` for this | Never. Additive only; this added no plan fields | Fake break |

### Reviewer questions

1. Does Channel still run without this contribution?
2. Does Motion still run without Channel?
3. Is the name still a contribution (`ux_motion.channel`), not Glue/Bridge/Adapter?
4. Does `applyOp("morph")` still go through `injectHtml`?
5. Did you add a plan field? If yes, it must be additive under `v: "1"`.

**End of council record.**
