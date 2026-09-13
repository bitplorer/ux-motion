# Glossary

| Term | Meaning in ux_motion |
|---|---|
| **Plan** | Root IR document (`v`, `id`, `root`, …) |
| **Node** | Any IR object with a `kind` |
| **Track** | One target + role + recipe |
| **Recipe** | from/to + timing (+ optional spring/path/morph.d) |
| **morph.d** | Soft 2: interpolate similar SVG path `d` (`morph_d`). Not `path` / along. |
| **Phase** | Mode container for children |
| **Group** | Named phase-like bag under `tracks` |
| **wait** | Mode: exits before enters for *direct* tracks (Soft 3 locked) |
| **wait bags** | `exits` / `stays` / `enters` / `nested` (`partition_wait`) |
| **wait clocks** | `exit_end` / `stay_end` / `enter_t` (`wait_clocks`) |
| **Presence** | Whether a target remains in the DOM and is marked present |
| **after** | End-of-track DOM fate: keep / remove / hide |
| **share** | Named identity continuity with client measurement (FLIP) |
| **bind** | Progress-driven tape wrapper |
| **scrub** | Seek a bind tape to progress 0..1 (`scrub` / `UxMotion.scrub`) |
| **Soft LOCK** | No gesture Soft here. Hover/tap/press/pan/drag → Channel Intent / Behavior `@action`. Leftover: [../OWNERSHIP.md](../OWNERSHIP.md) |
| **score** | Multi-hop hold key across Results |
| **cue** | Resolve a score |
| **send.play** | Emit transition.play Result |
| **send.update** | Emit classic DOM ops Result |
| **Reference player** | Python `interpret` — schedule contract |
| **Web player** | `UxMotion` JS runtime |
| **Token** | Named design-system duration/easing/distance/spring |
| **Pattern** | Helper that returns a full plan |
| **IR** | Intermediate Representation — the JSON plan shape |
| **Result** | Channel envelope `{ok, ops, meta?}` |
| **FLIP** | First, Last, Invert, Play — measurement technique for share |
| **WAAPI** | Web Animations API |
