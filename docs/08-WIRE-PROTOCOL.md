# Wire Protocol

## Transport assumption

Any channel that can deliver a JSON object with an `ops` array is sufficient. The library does not implement networking.

## Result document

```json
{
  "ok": true,
  "ops": [
    {
      "op": "transition.play",
      "plan": { "v": "1", "kind": "plan", "id": "nav", "root": { } },
      "meta": {
        "update": [ /* optional classic ops if also_update=True */ ]
      }
    }
  ],
  "meta": {
    "action": "optional-handler-name"
  }
}
```

## Operations

### transition.play

Full plan execution on a capable client.

### transition.rewind

Same as play but plan is pre-inverted by the server.

### transition.cancel

```json
{ "op": "transition.cancel", "id": "optional-plan-id" }
```

Clears queue and running animations.

### Classic projection (send.update)

| op | fields |
|---|---|
| `morph` | `target`, `html`, `morph: "idiomorph"` |
| `remove` | `target` |
| `set_attr` | `target`, `attrs` object |
| `noop` | `meta: { as: "update", empty: true }` |

## When html becomes a string

Authoring keeps ux-dom trees on `track.html`. The wire IR is strings only.
The conversion is ux-dom's official serialize, not an extra stringify:

```
HTMLResponse          stamp_tree → content.__render__()
Channel UxDomRenderer value.__render__()
Motion freeze / dumps / send.play / Scene.__render__
                      stamp_tree (if nonce) → html.__render__(pretty=False)
```

`Scene.__render__` emits `<script type="application/ux-motion+json">` with
the frozen plan (all fields, including serialized markup). The player boots
those scripts on `DOMContentLoaded` unless `data-play="false"`.

`document.use(Motion())` injects the player at
`/ux-pkg/ux-motion/static/ux-motion-player.js`.

## Client integration snippet

```html
<script src="/static/ux-motion-player.js"></script>
<script>
  // after receiving channel Result:
  UxMotion.applyOps(result.ops);
</script>
```

## Capability negotiation (host responsibility)

The **host** decides play vs update:

- Modern browser with player script → `send.play`
- Legacy / bot / no JS → `send.update`
- Optional: `send.play(..., also_update=True)` embeds classic ops in `meta.update` for gateways that strip unknown ops

The library does not fingerprint clients.
