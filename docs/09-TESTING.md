# Testing

## Run

```bash
cd ux_motion-1.0.0-complete
PYTHONPATH=. python -m unittest discover -s tests -v
```

## What tests guarantee

| Area | Guarantee |
|---|---|
| Classic wait | Enter starts after exit ends |
| share | IR kind present; schedule has share-leave/arrive; as_update projects |
| bind | Root kind bind; bookkeeping events |
| spring / along | Recipe carries spring/path |
| tokens | Presets resolve |
| rewind | Roles invert; op is transition.rewind |
| patterns | page/modal validate |
| reduce_tree | reduced=swap |
| frames | Returns SVG markup |
| schema | Enumerates share/bind/score/cue |
| duration cap | >120s raises PlanError |
| unknown kind | PlanError |
| roundtrip | dumps/loads preserves id |

## Contract you should add in your host

1. Snapshot `interpret` schedules for critical user flows (regression).
2. HTTP integration: POST play endpoint returns `transition.play`.
3. Optional Playwright: real FLIP rects for share scenes.

## Property ideas (not all in this package)

- Random trees: start ≤ end per target
- wait direct exits before enters
- as_update never contains transition.play
- validate idempotent
