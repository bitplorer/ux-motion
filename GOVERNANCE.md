# Governance

## Maintainer

[bitplorer](https://github.com/bitplorer) maintains this repository.

## Decisions

| Kind | How |
|------|-----|
| Ownership / layer boundary | Documented in the README ownership table and (for product composition) [ux-compose `docs/FLOW.md`](https://github.com/bitplorer/ux-compose/blob/main/docs/FLOW.md). Boundary changes need an ADR or equivalent explanation page. |
| Public API | Names in the package `__all__` (and the CLI entry point). Adding a name is a release note; removing one is a breaking change. |
| Docs | Diátaxis mode is sticky. Do not turn a reference page into a tutorial. |
| Security | Private report first. See [SECURITY.md](SECURITY.md). |

## Contributions

Pull requests are welcome. Review looks for:

1. Fail-closed behavior (no silent success on illegal input)
2. Tests for the residual you touched
3. Docs in the same change
4. No reimplementation of a sister layer

See [CONTRIBUTING.md](CONTRIBUTING.md) and [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md).

## Release

Pre-1.0 (`0.y.z`) may include breaking changes. Changelog follows Keep a Changelog.
