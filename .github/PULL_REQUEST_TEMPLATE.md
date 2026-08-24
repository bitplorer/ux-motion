## What

<!-- Public API, CLI, or doc path. -->

## Layer check

- [ ] This change belongs in **this** repository (ownership table in README).
- [ ] I did not reimplement a sister layer.

## Docs (Diátaxis)

- [ ] START_HERE still succeeds in five minutes if I touched onboarding.
- [ ] Reference matches `__all__` (no invented names).
- [ ] README links resolve to canonical pages (not `Moved` stubs).

## Tests

```bash
PYTHONPATH=. python -m unittest discover -s tests -v
```
