# Enhancements (API 1.0.0)

All enhancements are **additive** on IR v1.

---

## 1. share — shared presence (FLIP)

**Problem:** Fade/slide cannot express “this image is the same object on two pages.”

**IR:** `kind: "share"`, fields `id`, `leave`, `arrive`, `recipe`.

**Authoring:**

```python
scene("pdp").share("hero", leave="#grid-img", arrive="#pdp-img").play()
```

**Client:** Measure both rects; invert; animate arrive; hide leave.

**Update path:** set_attr on arrive + leave.

---

## 2. bind — scrubbable time

**Problem:** Fire-and-forget timelines cannot link to scroll or drag.

**IR:** `kind: "bind"`, fields `input`, `target`, `child`, optional `until`, `axis`.

**Authoring:**

```python
scene("essay").bind_to("scroll", "#article").enter("#fig", rise.enter()).play()
```

**Client (Soft 1):** `input=scroll` arms a paused WAAPI tape and a rAF scroll
loop. Progress (0..1) seeks `currentTime` and writes `data-uxm-progress`.
Hosts may also call `UxMotion.scrub(planId, progress)`. Python `scrub(plan, p)`
is the logical seek. `drag` remains one-shot (HOLD). No gesture APIs.

**Inputs:** `scroll` | `drag` | `progress`.

---

## 3. score + cue — multi-hop presence

**Problem:** Exit and enter need separate HTTP Results.

**IR:** `kind: "score"` with `phase`, and `kind: "cue"` with `score` id.

**Authoring:**

```python
# Result 1
scene("leave").as_score("checkout", phase="hold").exit("#cart", fade.exit()).play()

# Result 2
from ux_motion import cue, wait, rise
scene("arrive").also(
    cue("checkout"),
    wait(track("#pay", rise.enter())),
).play()
# or patterns:
multi_hop_leave(score_id="checkout", leave="#cart")
multi_hop_arrive(score_id="checkout", arrive="#pay")
```

**Client:** Hold map keyed by score id; cue resolves.

---

## 4. spring engine

**Recipe:**

```python
springy(preset="gentle")
fade.enter().with_spring("wobbly", stiffness=200)
scene("x").engine("spring").enter("#a", springy()).play()
```

**Presets (tokens):** snappy, gentle, wobbly, stiff — mass / stiffness / damping.

**JS:** Estimates duration from underdamped formula; clamps 120..2000 ms.

---

## 5. along(path)

```python
along("M0,80 C40,0 120,160 200,80", ms=600)
```

Sets recipe `path.d` and animates `offset` 0→1. JS sets `offset-path`.
Not SVG path `d` morph — that is `morph_d` (Soft 2).

---

## 5b. morph_d (Soft 2)

```python
morph_d("M0,0 L20,0 L20,20 Z", "M0,20 L20,0 L0,0 Z", ms=320)
fade.enter().with_morph_d(from_d, to_d)
```

**IR:** `recipe.morph.d.from` / `recipe.morph.d.to` (similar path strings).
Recipe name `"morph.d"`. `path` is not reused.

**Client:** WAAPI interpolates CSS `d`; commits the `d` attribute.
Soft 1 scrub KEEP. No gesture APIs. No Cap Host.

---

## 5c. wait completeness (Soft 3)

```python
from ux_motion import scene, fade, partition_wait, wait_clocks

plan = scene("nav").exit("#old", fade.exit(ms=100)).enter("#new", fade.enter(ms=80)).plan()
clock = wait_clocks(plan)
# clock.exit_end == 100; clock.enter_t == 100
```

**IR:** `phase.mode` / `group.mode` stay `"wait"`. No new keys.

**Bags:** `exits` / `stays` / `enters` / `nested` (`partition_wait` /
JS `partitionWait`). **Clocks:** `exit_end` / `stay_end` / `enter_t`.
Missing role is enter. Nested groups are not flattened. Not an
AnimatePresence dump.

Soft 1 scrub KEEP. Soft 2 `morph.d` KEEP. No gesture APIs. No Cap Host.

---

## 6. tokens

```python
tokens.ms("page")          # 360
tokens.ease("enter")
tokens.dist("md")          # 24
tokens.spring_params("snappy")
```

Prefer tokens in product code so timing stays coherent across the app.

---

## 7. when_reduce / reduce_tree

```python
scene("x").enter("#a", fade.enter(ms=300)).when_reduce(
    track("#a", none())
).play()
```

Sets `reduced: "swap"` and `reduce_tree`. Player uses alternate tree when OS prefers reduced motion.

---

## 8. rewind

```python
send.rewind(plan)
# or
scene("x").enter("#a", fade.enter()).rewind()
```

Inverts roles and from/to; op is `transition.rewind`.

---

## 9. patterns

| Function | Intent |
|---|---|
| `page` | Exit old, enter new |
| `modal` | Overlay + panel open/close |
| `toast` | Edge slide in/out |
| `list_stagger` | Staggered list |
| `shared_page` | Share + page fade |
| `multi_hop_leave` / `multi_hop_arrive` | Score pair |

---

## 10. schema()

Machine-readable JSON Schema of IR for cross-language authors.

---

## 11. frames()

Headless SVG timeline for CI and docs — no browser required.
