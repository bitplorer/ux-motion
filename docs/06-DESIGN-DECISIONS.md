# Design Decisions and Reasoning

Every non-trivial choice is recorded here so maintainers do not re-litigate settled questions.

---

## D1 — Server authors composition; client owns presence

**Decision:** Plans are pure data produced on the server. The client never invents enter/exit structure.

**Reasoning:** In channel/DOM stacks the server already owns the next UI state. Putting composition next to domain logic (Python) avoids a second source of truth in JS components.

**Rejected:** Client-only libraries that require React trees; dual authoring in TS + Python.

---

## D2 — JSON IR with additive versioning

**Decision:** Single major `v: "1"`. Unknown fields ignored. Keys never reused.

**Reasoning:** Channel peers upgrade independently. Additive evolution is the only strategy that survives years of partial deploys.

**Rejected:** Protobuf-only; pickle; breaking field renames inside v1.

---

## D3 — Intent verbs, not transport jargon

**Decision:** `send.play` / `send.update` / `send.rewind`. No `floor`, no `classic`, no `ChannelAdapter` in the public API.

**Reasoning:** Developers name *what they want*. Transport names rot and confuse.

**History:** Early drafts used `floor="web|classic|compat"`. Removed.

---

## D4 — wait partitions direct tracks only

**Decision:** Nested groups are independent units under wait.

**Reasoning:** Flattening nested sequences into a global exit bag destroys local choreography (e.g. a side-rail sequence running beside a main stage wait). Framer’s presence is per-subtree; we mirror that with explicit nesting.

**Rejected:** “Everything under wait is one global exit-then-enter bag.”

---

## D5 — layout ≠ FLIP

**Decision:** `role: "layout"` schedules as stay. True shared-element continuity is `kind: "share"`.

**Reasoning:** Advertising `layout` as FLIP without measurement is a lie. Share makes the client measurement contract explicit.

---

## D6 — Recipe names must do what they say

**Decision:** `rise.enter()` defaults y>0; `slide` defaults x; `blur` defaults blur radius.

**Reasoning:** A name that is only fade under the hood is a trap.

---

## D7 — Duration hard cap 120s

**Decision:** `PlanError` if recipe duration > 120000 ms.

**Reasoning:** Prevents accidental day-long WAAPI locks from bad data.

---

## D8 — as_update never drops tracks

**Decision:** Stagger and share project to set_attr/remove; empty yields explicit `noop`.

**Reasoning:** Silent data loss on the non-animated path is a production incident waiting to happen.

---

## D9 — Reference player is the contract

**Decision:** Python `interpret` defines order; JS must match order, not wall-clock.

**Reasoning:** Browser timing is not deterministic under load. Order is testable and sufficient for presence correctness.

---

## D10 — HTML is trusted server markup

**Decision:** No sanitizer in the library.

**Reasoning:** Same model as server-driven morph. Sanitization belongs at the boundary that accepts user content, not inside the motion plan.

---

## D11 — Spring as recipe metadata + engine hint

**Decision:** Spring params live on the recipe; plan.engine may be `"spring"`.

**Reasoning:** Allows per-track physics without a separate IR kind. JS estimates duration; full solver can improve later without breaking IR.

---

## D12 — Score for multi-hop, not one giant plan

**Decision:** Presence can span two HTTP Results via score/cue.

**Reasoning:** AnimatePresence in SPA never left the tab. Server-driven apps do. Holding exit nodes client-side until the next Result is the only correct model.

---

## D13 — Patterns are sugar, not new IR

**Decision:** `page`, `modal`, etc. compile to ordinary plans.

**Reasoning:** Keeps the IR small. Patterns can evolve without wire changes.

---

## D14 — No React / no TypeScript core

**Decision:** Python + vanilla JS player only.

**Reasoning:** Product constraint of the host stack (ux-dom + ux-channel). A React adapter could exist later as a separate package consuming the same IR.

---

## D15 — Empty scene is an error

**Decision:** `plan()` raises if no tracks.

**Reasoning:** An empty plan is almost always a builder bug. Fail loud.

---

## D16 — MotionChannel is a contribution, not Glue / Bridge / Adapter (1.3.0)

**Decision:** `document.use(Motion(), MotionChannel())` injects
`ux-motion-channel.js`. The hook peels `transition.*` on
`channel:beforeApply` and plays them on `channel:afterApply`. Channel
never learns those ops. Player `applyOp("morph")` uses `injectHtml`.
IR stays `"1"`.

**Reasoning:** A Result may carry authority morph and motion. Channel
`applyOp` must stay ignorant of plans so Motion is droppable. Playing
motion *before* morph, or injecting HTML for a just-morphed target,
remounts identified images. A Host file named `glue.js` steals a
reserved word (Glue = `ux_channel_ux_dom`). A new repo for 40 lines of
JS is package explosion. Owner belongs in `name="ux_motion.channel"`.

**Rejected:** Teaching Channel `transition.*`; Host `glue.js`; calling
it a Bridge; JS in `ux_app.adapter`; `ux_channel_ux_motion` as a repo;
player `innerHTML` for `morph`.

**Reopen:** only if the hook grows a Python interop surface (then a
glue package named after both peers is legal), or Channel adds a
first-class compositor that makes the contribution redundant. Never
rename to glue/Bridge/Adapter. Never play before authority morph.

See [14-CHANNEL-COMPOSITOR.md](14-CHANNEL-COMPOSITOR.md).

