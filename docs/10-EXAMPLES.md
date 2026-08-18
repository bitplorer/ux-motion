# Examples

## Page transition

```python
from ux_motion import scene, fade, rise, send

result = (
    scene("page")
    .exit("#view-a", fade.exit(), after="hide")
    .enter("#view-b", rise.enter())
    .play()
)
```

## Shared hero

```python
from ux_motion import scene, shared_page

plan = shared_page(
    share_id="hero",
    leave_img="#grid .thumb",
    arrive_img="#pdp .hero",
    leave_page="#grid",
    arrive_page="#pdp",
)
```

## Modal

```python
from ux_motion import modal, send

send.play(modal(overlay="#overlay", panel="#dialog", open_=True))
send.play(modal(overlay="#overlay", panel="#dialog", open_=False))
```

## Staggered list

```python
from ux_motion import scene, rise

scene("inbox").stagger_in(".row", rise.enter(), gap_ms=40).play()
```

## Scroll-linked figure

```python
from ux_motion import scene, rise

scene("story").bind_to("scroll", "#article").enter("#figure", rise.enter(ms=400)).play()
```

## Multi-hop checkout

```python
from ux_motion import multi_hop_leave, multi_hop_arrive, send

# after "continue" action — first response
send.play(multi_hop_leave(score_id="co", leave="#cart-step"))

# after server computes payment step — second response
send.play(multi_hop_arrive(score_id="co", arrive="#pay-step"))
```

## Path tip (river.ai style)

```python
from ux_motion import scene, along

scene("reward").enter("#dot", along(
    "M10,90 C40,10 80,10 120,90 S200,170 240,90",
    ms=800,
)).play()
```

## Spring card

```python
from ux_motion import scene, springy

scene("deal").engine("spring").enter("#card", springy(preset="snappy")).play()
```

## Inspect schedule

```python
from ux_motion import scene, fade, explain, frames, interpret

plan = scene("x").exit("#a", fade.exit(ms=100)).enter("#b", fade.enter(ms=100)).plan()
print(explain(plan))
open("schedule.svg", "w").write(frames(plan))
for e in interpret(plan):
    print(e)
```

## Reduced motion alternate

```python
from ux_motion import scene, fade, track, none

scene("x").enter("#box", fade.enter(ms=400)).when_reduce(
    track("#box", none())
).play()
```

## DOM-only client

```python
from ux_motion import scene, fade

result = scene("x").exit("#a", fade.exit()).enter("#b", fade.enter(), html="<section>Hi</section>").update()
# ops are morph/remove/set_attr only
```
