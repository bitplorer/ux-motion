# Composition Semantics

These rules are the heart of the library. The reference player (`interpret`) **is** the definition. The JS player must match start/end **order**.

---

## Modes

### `parallel`

Every child starts at the same logical `t0` (plus optional `i * stagger_ms` on phases).

```
t0: A start, B start
t0+durA: A end
t0+durB: B end
```

Span = max of child ends.

### `sequence`

Children run one after another. Child i starts when child i-1 ends (plus optional phase `stagger_ms` gap).

```
t0: A start
tA: A end = B start
tB: B end
```

### `wait` (presence mode)

**Only applies to direct track/stagger children.** Nested groups/phases/shares/binds/scores are **nested units** and start at `t0` independently (they are not shoved into the exit bag).

Partition of **direct** track/stagger children:

1. **exits** (`role == "exit"`) — all start at `t0`; `exit_end = max(end)`
2. **stays / layout** — start at `exit_end`
3. **enters** — start at `stay_end` (which is `exit_end` if no stays, or after stays)
4. **nested** (anything that is not track/stagger) — each starts at `t0` in parallel with exits

```
t0: all exits + all nested groups
exit_end: stays start
stay_end: enters start
```

If there are **no** exits and **no** stays, enters start at `t0`.

This is the AnimatePresence insight expressed as data: **exits complete before enters**, without flattening nested choreography.

---

## Nested groups are not flattened

```python
wait(
  group("stage", exit_A, enter_A, mode="wait"),
  sequence(exit_B, enter_B),
)
```

- `group("stage")` is nested → runs its own internal wait from t0.
- `sequence(...)` is nested → runs from t0 in parallel with the stage group.
- Direct tracks on the outer wait would be partitioned; here there are none.

**Wrong mental model:** “everything in a wait is global exit-then-enter.”  
**Right mental model:** “wait partitions **siblings that are tracks**; nested nodes are independent units.”

---

## Roles

| Role | Typical after | Schedule bag under wait |
|---|---|---|
| `exit` | `remove` or `hide` | exits |
| `enter` | `keep` | enters |
| `stay` | `keep` | stays (after exits) |
| `layout` | `keep` | stays (same bag; **not** FLIP — use `share`) |

---

## After

| Value | Player effect at end of track |
|---|---|
| `keep` | Leave node in DOM |
| `remove` | `parent.removeChild` |
| `hide` | `hidden=true` + `aria-hidden=true` |

---

## Stagger expansion

Reference player: for selector S and count N (from `counts` or default 3):

```
start_i = t0 + delay + i * gap_ms
end_i   = start_i + duration
target  = f"{S}[{i}]"
```

JS player: queries `document.querySelectorAll(S)` and uses real length; delay same formula.

---

## Share timing

Share is a single span:

```
t0: leave start, arrive start (roles share-leave / share-arrive)
t0+duration: both end
```

Physical FLIP uses measured rects; logical duration comes from recipe.

---

## Bind / score / cue in the schedule

They emit bookkeeping events `@bind:…`, `@score:…`, `@cue:…` bracketing the child span so `explain` and tests can see them. Child schedule is unchanged relative to t0.

---

## Rewind inversion rules

| Original | Inverted |
|---|---|
| enter track | exit track (after remove if was keep) |
| exit track | enter track (after keep) |
| from/to | swapped |
| `name` ending `.enter` / `.exit` | flipped |
| group/phase children | reversed order + each inverted |
| share leave/arrive | swapped |

Rewind emits `transition.rewind` with the inverted plan (id suffixed `__rewind`).

---

## Reduced motion

| `reduced` | Behavior |
|---|---|
| `skip` | Duration/delay → 0 |
| `simplify` | Cap duration at 80ms |
| `honor` | Play full recipe even if OS prefers reduced |
| `swap` | If OS prefers reduced and `reduce_tree` present, play that tree with skip |

---

## Interrupt edge cases

- `replace` cancels by **target key**, not by plan id.
- `queue` is FIFO; `cancel` clears the queue.
- `ignore` only dedupes **same plan id** already in `playing`.

---

## as_update projection rules

| Node | Ops |
|---|---|
| enter + html | `morph` |
| enter no html | `set_attr` present=1 |
| exit after remove | `remove` |
| exit after hide | `set_attr` hidden |
| stagger enter | `set_attr` on selector |
| stagger exit remove | `remove` on selector |
| share | set arrive present+share id; leave present=0 |
| nothing matched | `noop` |

**Stagger is never dropped silently.**
