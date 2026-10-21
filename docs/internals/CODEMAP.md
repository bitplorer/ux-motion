# Code map — `codemap/`

> **Diátaxis:** explanation · **Layer:** ux-motion
> Map: [../INDEX.md](../INDEX.md).

[`codemap/`](codemap/index.json) is a generated, machine-readable map of
`ux_motion`, one JSON shard per module and per player script: layers, imports,
symbols, the public API, features and the domain charter. CI fails when it is
stale or when the map has a problem.

[`scripts/codemap.py`](../../scripts/codemap.py) is vendored byte-identical
from ux-dom; `index.json` records its version and sha256. The full reference
(fields, config keys, checks) is ux-dom's
[CODEMAP.md](https://github.com/bitplorer/ux-dom/blob/main/docs/internals/CODEMAP.md).

## Rule

A PR updates the map in the same change as the code:

```bash
git add <new files>                      # consumers are read from tracked files
python scripts/codemap.py --write-changed
python scripts/codemap.py --check
```

## What is curated here

| File | Content |
|------|---------|
| `[tool.codemap]` in [pyproject.toml](../../pyproject.toml) | One layer per module; `layer_rules` are the allowed-imports graph of [01-ARCHITECTURE.md](../01-ARCHITECTURE.md) |
| [features.toml](features.toml) | Features → modules, player scripts, symbols, tests, docs |
| [domain.toml](domain.toml) | What this library owns, its public facade, non-goals, and the exact ux-dom names it may use |

A new import between `_`-modules that the architecture graph does not allow
fails `--check`: change the graph in 01-ARCHITECTURE.md and `layer_rules`
together, or do not add the import.
