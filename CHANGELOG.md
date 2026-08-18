# Changelog

All notable changes to **ux_motion** are documented here.

Versioning follows Semantic Versioning for the library API (API_VERSION / __version__).
The plan IR uses a separate major (IR_VERSION / plan field v). See docs/13-VERSIONING.md.

---

## 1.0.0 — 2026-08-18

First public release of **ux_motion** as a complete library.

### Library

- Python facade: scene, recipes, send.play / send.update / send.rewind / send.cancel
- IR v1: plan, phase, group, track, stagger, share, bind, score, cue
- Composition modes: wait, sequence, parallel with nested-group independence
- Recipes: fade, rise, slide, scale, blur, none, snap, along(path), springy
- Design tokens, patterns, reference player, classic projection, JSON Schema
- Vanilla JS player: static/ux-motion-player.js (UxMotion.version == 1.0.0)

### Docs

- Overview, architecture, IR spec, API reference, composition semantics
- Player contract, design decisions, enhancements, wire protocol
- Testing, examples, glossary, Mermaid diagram set, versioning policy

### Compatibility

- Plan wire field v must be "1"
- Unknown IR fields are ignored by validators and should be ignored by receivers
