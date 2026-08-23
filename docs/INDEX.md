# ux-motion documentation index

**Start:** [../START_HERE.md](../START_HERE.md)
**Complete overview:** [00-OVERVIEW.md](00-OVERVIEW.md)

Numbered `00`–`14` is the systematic set (kept). This file assigns **audience**
and **Diátaxis mode**. It does not replace those files.

## Folder contract (Phase 2)

| Folder | Diátaxis mode | May contain | Must not contain |
|--------|---------------|-------------|------------------|
| `docs/guides/` | how-to | Goal-oriented recipes | Conceptual essays as primary form |
| `docs/reference/` | reference | Facts, signatures, tables | Learning narrative as primary form |
| `docs/internals/` | explanation | Why, architecture, C4 | Step lists as primary form |
| `docs/examples/` | examples | Worked recipes / pointers | Law |
| `docs/adr/` | ADR | Decisions (or an index of them) | Mixed how-to |

Specialized folders (`security/`, `ship/`, `design/`, `tutorial/`, `patterns/`, `archive/`) stay.
`docs/INDEX.md` is the map. Do not add a second competing map.


This layer owns presence/transition plans as data.
It does **not** own product behavior or DOM construction.

---

## Audience

| You are… | Start (≤ 2 clicks from repo root) |
|----------|-----------------------------------|
| **New** | [../START_HERE.md](../START_HERE.md) |
| **Need the whole product description** | [00-OVERVIEW.md](00-OVERVIEW.md) |
| **Implementing / changing IR** | [02-IR-SPEC.md](02-IR-SPEC.md) · [03-API-REFERENCE.md](03-API-REFERENCE.md) |
| **Changing MotionChannel** | [14-CHANNEL-COMPOSITOR.md](14-CHANNEL-COMPOSITOR.md) |
| **Maintainer / agent** | [../AGENTS.md](../AGENTS.md) · [../CONTRIBUTING.md](../CONTRIBUTING.md) |

---

## By Diátaxis mode

### Tutorial

| Doc | Contents |
|-----|----------|
| [../START_HERE.md](../START_HERE.md) | 5-minute path |
| [examples/README.md](examples/README.md) | Example slot |
| [10-EXAMPLES.md](10-EXAMPLES.md) | End-to-end recipes |
| [../examples/minimal.py](../examples/minimal.py) | Runnable sample |

### How-to

| Doc | Contents |
|-----|----------|
| [guides/README.md](guides/README.md) | How-to slot → numbered 07 / 09 / 13 / 14 |
| [09-TESTING.md](09-TESTING.md) | How to run tests; what they guarantee |
| [13-VERSIONING.md](13-VERSIONING.md) | Semver policy, IR vs API, release checklist |
| [07-ENHANCEMENTS.md](07-ENHANCEMENTS.md) | share, bind, score, spring, along, tokens, rewind, patterns |
| [14-CHANNEL-COMPOSITOR.md](14-CHANNEL-COMPOSITOR.md) | How to change MotionChannel later |

### Reference

| Doc | Contents |
|-----|----------|
| [reference/README.md](reference/README.md) | Reference slot → numbered 02–05 / 08 / 11 |
| [02-IR-SPEC.md](02-IR-SPEC.md) | Every IR field, kind, enum, validation rule |
| [03-API-REFERENCE.md](03-API-REFERENCE.md) | Every public symbol |
| [04-COMPOSITION-SEMANTICS.md](04-COMPOSITION-SEMANTICS.md) | wait / sequence / parallel / nested groups |
| [05-PLAYER-CONTRACT.md](05-PLAYER-CONTRACT.md) | Reference player + JS player obligations |
| [08-WIRE-PROTOCOL.md](08-WIRE-PROTOCOL.md) | Ops, Result shape, classic projection |
| [11-GLOSSARY.md](11-GLOSSARY.md) | Terms |
| [../CHANGELOG.md](../CHANGELOG.md) | History (not current teaching) |

### Explanation

| Doc | Contents |
|-----|----------|
| [internals/README.md](internals/README.md) | Explanation slot → 00 / 01 / 12 |
| [internals/c4.md](internals/c4.md) | C4-style context / containers |
| [00-OVERVIEW.md](00-OVERVIEW.md) | Full product description |
| [01-ARCHITECTURE.md](01-ARCHITECTURE.md) | Layers, modules, dependency graph, data flow |
| [adr/README.md](adr/README.md) | ADR slot → 06 / 14 / 13 |
| [06-DESIGN-DECISIONS.md](06-DESIGN-DECISIONS.md) | Why each design choice; rejected alternatives |
| [12-DIAGRAMS.md](12-DIAGRAMS.md) | Mermaid for every concept |

---

## Sister layers

| Package | Role |
|---------|------|
| [ux-dom](https://github.com/bitplorer/ux-dom) | Render / Document |
| [ux-channel](https://github.com/bitplorer/ux-channel) | Intent → Cap → Result |
| [ux-behavior](https://github.com/bitplorer/ux-behavior) | Product behavior → Ops |
| [ux-compose](https://github.com/bitplorer/ux-compose) | Composition + product CLI |

Do not flatten these layers into this repo.

