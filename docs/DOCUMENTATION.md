# Documentation standard

This file is the **family documentation contract** for the UX stack
(`ux-dom`, `ux-channel`, `ux-behavior`, `ux-motion`, `ux-fnbase`, `ux-compose`).
It is the improved prompt we actually run: research first, then write, then
verify against code.

Out of scope for this round: `ux-app`, `ux-motion-lib`.

See the same contract in any sister repo under `docs/DOCUMENTATION.md`.

## Research bar

[Diátaxis](https://diataxis.fr/) four types. [Standard Readme](https://github.com/RichardLitt/standard-readme/blob/main/spec.md) section order, License last. [GitHub community health files](https://docs.github.com/en/communities/setting-up-your-project-for-healthy-contributions/creating-a-default-community-health-file). Keep a Changelog + SemVer. Gold READMEs: FastAPI, httpx, pydantic.

## Audiences

First-time user → `START_HERE.md`. Experienced → how-to + reference. Contributor → `CONTRIBUTING.md`. Security → `SECURITY.md`. Operator → doctor / verify. Agent → `docs/INDEX.md` + `__all__`.

## Accuracy

Public names from `__all__`. Versions from `pyproject.toml`. If code and docs disagree, code wins — then fix the doc in the same change. Never cite a `Moved` stub as canonical.

## Push

GitHub connector only. One agent. One repository at a time. Do not document `ux-app` or `ux-motion-lib` in this pass.
