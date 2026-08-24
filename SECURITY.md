# Security Policy

## Supported versions

| Version | Supported |
|---------|-----------|
| 1.3.x   | Yes |
| < 1.3   | Best-effort (upgrade; IR v1 is additive) |

## Threat model

**ux-motion authors plans as data.** A Plan is JSON IR v1 that a player interprets. This layer does **not** authenticate users, mint Caps, or escape HTML.

| In scope for this repo | Out of scope (sister / host) |
|------------------------|------------------------------|
| Plan validation (`validate_plan` / `PlanError`) | Capability tokens (`ux-channel`) |
| Fail-closed unknown IR kinds | Product `@action` authorization (`ux-behavior`) |
| Keeping ux-dom trees as trees until official serialize | XSS of `html=` payloads — the **host** must escape / CSP |
| Player contract (play / cancel / rewind) | Document CSP (`ux-dom`) |

`html=` on a track is markup the host already decided to send. Treat it like any other hypermedia fragment: nonce CSP, no `javascript:` URLs, caller-escaped user content.

## Reporting

Report vulnerabilities **privately**:

1. GitHub Security Advisory on [bitplorer/ux-motion](https://github.com/bitplorer/ux-motion/security/advisories/new), or
2. Email **bitplorer@outlook.com** with subject `ux-motion security`

Include version / commit, a minimal Plan or script, and impact (player crash, unexpected DOM write, prototype confusion).

Do **not** open a public issue for unreleased vulnerability details.

We aim to acknowledge within 5 business days.
