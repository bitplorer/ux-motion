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

**Client:** Marks host; scroll listener writes `data-uxm-progress`. Child still has a full schedule for one-shot play.

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
