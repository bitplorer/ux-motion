# API Reference (public facade)

All symbols below are exported from `ux_motion`. Signatures use Python 3.10+ typing.

---

## Version and contract

| Symbol | Type | Value / role |
|---|---|---|
| `API_VERSION` | `str` | `"1.3.0"` |
| `IR_VERSION` | `str` | `"1"` |
| `CONTRACT` | `dict` | Laws, kinds, modes, roles, engines, op names |
| `PlanError` | `Exception` | Raised on invalid IR / JSON |

---

## Scene builder

### `scene(sid: str | None = None) -> Scene`

Create a fluent scene. If `sid` is omitted, a random `scene-<hex10>` id is assigned.

### `Scene` methods (all return `self` unless noted)

| Method | Effect |
|---|---|
| `interrupt(policy)` | Set `replace\|queue\|ignore` |
| `reduced(policy)` | Set `skip\|simplify\|honor\|swap` |
| `engine(name)` | Set `presence\|view\|spring` |
| `on_complete(action)` | Set plan.complete string |
| `when_reduce(*nodes)` | Set `reduce_tree`; forces `reduced="swap"` |
| `wait()` / `parallel()` / `sequence()` | Set root phase mode |
| `also(*nodes)` | Append pre-built nodes |
| `named(name, mode="wait")` | Open a named group; subsequent tracks go inside until next mode/also/named/plan |
| `exit(target, recipe, *, after="remove", html=None)` | Add exit track |
| `enter(target, recipe, *, after="keep", html=None)` | Add enter track. `html` may be a ux-dom tree; it stays a tree until serialize |
| `stay(target, recipe)` | Add stay track |
| `stagger_in(selector, recipe, *, gap_ms=40)` | Stagger enter |
| `stagger_out(selector, recipe, *, gap_ms=30)` | Stagger exit |
| `share(sid, *, leave, arrive, recipe=None)` | Shared element |
| `bind_to(input, target, *, until=None, axis=None)` | Wrap entire scene root in bind |
| `as_score(sid, *, phase="now")` | Wrap entire scene root in score |
| `plan() -> dict` | Compile + validate (BUILD; trees stay); raises if empty |
| `ops() -> list` | `transition.play` ops only |
| `play(*, also_update=False, action=None) -> dict` | Result via `send.play` (freezes on the wire) |
| `update(*, action=None) -> dict` | Result via `send.update` |
| `rewind(*, action=None) -> dict` | Result via `send.rewind` |
| `cancel_ops() -> list` | `transition.cancel` for this id |
| `iter_markup()` | Live `html` values still on this scene (trees or strings) |
| `tag()` | ux-dom Component face (soft-dep; does not re-parent trees) |
| `__render__` / `__html__` / `__str__` | Official serialize: frozen plan as `<script type="application/ux-motion+json">` |
| `__iter__` | Yields `tag()` so `div(scene)` works without patching ux-dom |

---

## Functional constructors

```python
track(target, recipe, *, role="enter", after=None, html=None, name=None) -> dict
stagger(selector, recipe, *, role="enter", gap_ms=40, after="keep") -> dict
share(sid, *, leave, arrive, recipe=None) -> dict
bind(input_name, target, child, *, until=None, axis=None) -> dict
score(sid, child, *, phase="now") -> dict
cue(score_id, child=None) -> dict
group(name, *children, mode="wait", tracks=None) -> dict
wait(*children) -> dict
sequence(*children) -> dict
parallel(*children, stagger_ms=0) -> dict
```

These return **raw node dicts** (not yet a full plan). Compose with `scene().also(...)` or nest inside group/phase.

---

## Recipes

### Families

Each of `fade`, `rise`, `slide`, `scale`, `blur` is a family with:

```python
family.enter(*, y=None, x=None, scale=None, opacity=None, blur=None,
             ms=None, delay=0, easing=None, rotate=0) -> Recipe
family.exit( same parameters ) -> Recipe
```

**Defaults that make the name true:**

| Family | enter default | exit default |
|---|---|---|
| `fade` | opacity 0 → 1 | opacity 1 → 0 |
| `rise` | y = +16 | y = -12 |
| `slide` | x = +24 | x = -24 |
| `scale` | scale 0.94, opacity 0 | scale 0.96, opacity 0 |
| `blur` | blur 8, opacity 0 | blur 8, opacity 0 |

`ms` defaults come from `tokens.ms("enter")` / `tokens.ms("exit")`.

### Special recipes

```python
none(*, ms=0) -> Recipe          # instant / reduced
snap() -> Recipe                 # none(0)
along(path_d, *, ms=None, delay=0, easing=None, rotate="auto", opacity_from=0) -> Recipe
springy(*, y=None, x=None, scale=None, preset="snappy", ms=None) -> Recipe
```

### `Recipe` methods

```python
rec.with_delay(ms) -> Recipe
rec.with_duration(ms) -> Recipe
rec.with_easing(easing) -> Recipe
rec.with_spring(name="snappy", **params) -> Recipe
rec.with_path(d, *, rotate="auto") -> Recipe
```

`Recipe` is a `dict` subclass — JSON-serializable as-is.

---

## Tokens

```python
tokens.ms(name) -> int
tokens.ease(name) -> str
tokens.dist(name) -> float
tokens.spring_params(name="snappy") -> dict
tokens.as_dict() -> dict
```

Presets defined in `_tokens.py`: durations (`instant`, `fast`, `enter`, `exit`, `page`, `modal`, `stagger`, `spring`), easings, distances (`xs`…`xl`), springs (`snappy`, `gentle`, `wobbly`, `stiff`).

---

## Send / ops

```python
send.play(plan, *, also_update=False, action=None) -> Result
send.update(plan, *, action=None) -> Result
send.rewind(plan, *, action=None) -> Result
send.cancel(plan_id=None, *, action=None) -> Result

play(plan, *, meta=None) -> list[op]          # low-level ops only
cancel(plan_id=None, *, meta=None) -> list[op]
rewind(plan, *, meta=None) -> list[op]
rewind_plan(plan) -> plan                     # inverted plan dict
as_update(plan) -> list[op]                   # morph/remove/set_attr
to_result(ops, *, ok=True, action=None) -> Result
```

**Result shape:**

```json
{ "ok": true, "ops": [ /* op objects */ ], "meta": { "action": "..." } }
```

`meta` only present if `action` passed.

**Op types:**

| `op` | Fields |
|---|---|
| `transition.play` | `plan`, optional `meta` |
| `transition.rewind` | `plan` (already inverted), optional `meta` |
| `transition.cancel` | optional `id` |
| `morph` | `target`, `html`, `morph` |
| `remove` | `target` |
| `set_attr` | `target`, `attrs` |
| `noop` | `meta` (empty update) |

---

## Inspection

```python
validate_plan(plan) -> dict
compile_plan(plan, *, freeze=False) -> dict   # BUILD; freeze=True → freeze_plan
freeze_plan(plan) -> dict      # SERIALIZE: stamp_tree + __render__, then string IR
render_markup(node, *, pretty=False) -> str   # official serialize of one tree
as_html(node) -> str           # alias of render_markup
interpret(plan, *, counts=None) -> list[Event]
span_ms(plan, *, counts=None) -> int
explain(plan, *, counts=None) -> str
frames(plan, *, width=640, height=120, counts=None) -> str  # SVG
schema() -> dict                    # JSON Schema
dumps(plan, *, indent=2) -> str     # freeze then JSON
loads(text) -> dict
```

`html` on a track may be a ux-dom Component (or any object with `__render__` / `__html__`) until `freeze_plan` / `dumps` / `send.play` / `Scene.__render__`. The wire IR is strings only.

### `Event`

```python
@dataclass(frozen=True)
class Event:
    t: int          # ms
    event: str      # "start" | "end"
    target: str
    role: str
    name: str = ""
```

`counts` maps stagger selectors → element count for the reference player.

---

## Patterns

```python
page(*, leave, arrive, name="page", exit_ms=None, enter_ms=None) -> plan
modal(*, overlay, panel, name="modal", open_=True) -> plan
toast(*, target, name="toast", show=True) -> plan
list_stagger(*, selector, name="list", enter=True, gap_ms=None) -> plan
shared_page(*, share_id, leave_img, arrive_img, leave_page, arrive_page, name="shared-page") -> plan
multi_hop_leave(*, score_id, leave, name="hop-leave") -> plan
multi_hop_arrive(*, score_id, arrive, name="hop-arrive") -> plan
```

All return **validated plans** ready for `send.play`.

---

## Higher-order functions (trees → Scene)

These stay in BUILD. Call `.play()` / `dumps` / `__render__` to serialize.

```python
appear(tree, *, into=None, using=None, stagger=None, gap_ms=None, name="appear") -> Scene
swap(host, tree, *, using=None, stagger=None, gap_ms=None, share=None, name="swap") -> Scene
leave(target, *, using=None, after="hide", name="leave") -> Scene
sheet(overlay, panel="#sheet-panel", *, open_=True, name="sheet") -> Scene
notice(tree, *, show=True, name="notice") -> Scene
staggered(host, children=".tile", *, using=None, gap_ms=None, enter=True, name="list") -> Scene
hop.leave(score_id, target, *, using=None) -> Scene
hop.arrive(score_id, target, *, using=None) -> Scene
css_target(node) -> str
```

`using=` is a Recipe or a family (`rise`, `fade`, …). `share=` is `"sku"` or `(id, leave, arrive)`.

Recipe families are callable:

```python
rise(tree)                 # Scene — appear with rise.enter()
rise(tree, ms=180, stagger=".tile")
rise(ms=180)               # Recipe — same as rise.enter(ms=180)
fade(tree, role="exit")    # Scene — leave
```

Decorator (do not decorate views that also render into a Document):

```python
@motion(into="#view", stagger=".tile")
def shop():
    return section(..., id="view")

shop().play()
shop.view()   # original callable
```

---

## Presence helpers

```python
stamp(html: str, uid: str) -> str     # inject data-uxm-id (escaped)
region(uid, body="", *, cls="", tag="div") -> str
Presence().mark(uid) / .drop(uid) / .is_present(uid) / .clear() / .all()
```

---

## Motion namespace / Document runtime

`Motion.scene`, `Motion.track`, `Motion.share`, … mirror the functional API for hosts that prefer `Motion.*` style. `Motion.play` is `send.play`.

`document.use(Motion())` is a ux-dom contribution runtime:

- `document_head()` injects `<script src="/ux-pkg/ux-motion/static/ux-motion-player.js" defer>`
- `served_files()` exposes the package-owned player via `SafeStaticFile`

`document.use(MotionChannel())` is a second contribution (`name="ux_motion.channel"`):

- Injects `ux-motion-channel.js`
- `channel:beforeApply` peels `transition.*` into `result._uxMotion`
- `channel:afterApply` calls `UxMotion.applyOps` so Channel idiomorph wins the slot first
- Does not import `ux_channel`. Event names are public Channel API
- Not Glue (`ux_channel_ux_dom`), not a Bridge, not an Adapter

Use `MotionChannel` only when Channel applies the Result. Motion without
Channel still plays via `UxMotion.applyOps` / embedded plan scripts.

ux-dom is a soft dependency. Scene authoring and `Scene.__render__` work without it.

---

## Constants

```python
OP_PLAY = "transition.play"
OP_CANCEL = "transition.cancel"
OP_REWIND = "transition.rewind"
```
