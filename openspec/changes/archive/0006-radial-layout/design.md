# Design — 0006 Radial layout

## Model

```python
@dataclass(frozen=True)
class Radial:
    hub: str
    radius: float | None = None   # None -> derived from hub size + gap
    start: float = -90.0          # degrees
    dock: bool = False
    gap: float = 70.0
```

`Diagram` gains `radial: Radial | None = None`. `None` means "no radial
instruction" — the stack/layered engines run.

## Parser

Grammar (one per line):

```
radial hub=<id> [radius=<n>] [start=<n>] [dock] [gap=<n>]
```

Two regexes: a head for the keyword and the required `hub=`, plus a generic
attribute scan for `radius`/`start`/`gap` (numeric) and the `dock` flag.

- `hub=` missing/wrong → warning, `radial` dropped (falls back to stack).
- `radius`/`start`/`gap` non-numeric → warning, that attribute ignored (default
  kept).
- `dock` present without a value; on a non-polygon hub it is kept in the model
  but the layout warns and ray-casts.

Only the **first** `radial` line is honored; later lines warn.

## Layout

New engine `layout/radial.py`: `layout(diagram, theme) -> (diagram, w, h)` with
the same signature as `stack.layout`.

1. **Hub** = the node whose id is `radial.hub`. Members = all other top-level
   items (standalone nodes + groups) in declaration order.
2. **Radius** = `radial.radius` if given, else
   `hub_half_extent + gap + max_member_half_extent`.
3. Angle of member *i* of *n*: `start + i * 360 / n` (degrees → radians). A
   single member uses `start`. Placement is **clockwise** for increasing index.
4. Each member is centered on the ring; the hub is centered in the canvas.
5. Canvas is sized to the bounding box of hub + members + margin; the hub is at
   the canvas center so the ring fits.
6. Groups: a group member's frame is placed on the ring; its member nodes are
   placed inside the frame with the shared `_place_members` grid helper from
   `stack`.

### Polygon-face docking

When `radial.dock` is set **and** the hub is a polygon shape
(`polyN`; and the flat-sided `hex`/`diamond` as polygon-equivalent), each spoke
leaves from a **distinct face**: faces are evenly split across the polygon's
sides, and the docking point on a face is chosen by projecting the spoke's
direction onto that face. Non-polygon hubs ray-cast from center (a `dock` flag
on such a hub warns).

Docking is a **rendering concern**: the layout only positions boxes; the
renderer asks geometry for the anchor. So `geometry.py` gains:

```python
def dock_anchor(node, tx, ty, face_index, face_count) -> tuple[float, float]
```

which picks the polygon edge whose outward normal best matches the direction to
`(tx, ty)`, then returns the point on that edge nearest the ray — deterministically.
The renderer only uses `dock_anchor` for hub→spoke edges when the diagram is
radial with `dock`; otherwise the existing `anchor` is used.

Wait — the renderer is engine-agnostic and has no access to "which face". To keep
it simple and deterministic, docking is implemented as a **layout-side** decision
that biases spoke attachment: the layout records, per hub edge, nothing extra.
Instead the renderer detects a radial diagram from the model and, for edges
incident to the polygon hub, uses `dock_anchor` with the face index derived from
the spoke angle. See "Renderer" below.

### Hexagon geometry correction

While wiring docking, the `hex` shape was found to disagree between rendering and
geometry: the renderer draws a **full-width flat-topped** hexagon (slanted sides
inset by 20px), while geometry treated `hex` as a **regular polygon inscribed in
the node's square box** (radius `min(w, h) / 2`). Anchors therefore landed
*inside* the drawn hexagon and connectors stopped in empty space.

Fix: `geometry.hex_vertices` returns the exact flat-topped hexagon the renderer
draws (single source of truth, reused by the renderer); `polygon_vertices`,
`anchor` and `vertical_anchor` route `hex` through it. This also corrects
`shapes.fl` (change 0002): its hex→pill connector now leaves the bottom flat
edge instead of an interior vertex. `dock_anchor` clamps the crossing to the
actual edge segment (smallest positive `t` with `0 <= u <= 1`), so a diagonal ray
through a vertex picks a well-defined face instead of escaping the shape.

The `shapes.svg` golden (0002) is regenerated to reflect the corrected hexagon;
all other goldens (0001, 0003–0005) are byte-identical.

## Renderer

`svg._edges` already resolves anchors via `shapes.anchor`. For a **radial +
dock** diagram, an edge whose hub endpoint is a polygon gets
`shapes.dock_anchor(hub, other_center, face_index, face_count)` where
`face_index` is computed from the outgoing direction. To keep the renderer pure
and engine-agnostic, this is gated on the model: the renderer reads
`diagram.radial` and, for the hub node when `dock`, uses `dock_anchor`; all other
edges keep `anchor`. This is a small, contained branch.

## Compiler

`compile_diagram` picks the engine, precedence radial → layered → stack:

```python
if diagram.radial:
    engine = radial
elif diagram.layers:
    engine = layered
else:
    engine = stack
```

This keeps 0001–0005 byte-identical when neither instruction is present.

## Determinism

Member order = declaration order; angles = `start + i*360/n`; docking face =
`round(angle / step) % sides` with a stable tie-break by face index. No
randomness, no hash ordering.

## Test strategy

- Parser: `radial hub=a` parsed; missing/unknown hub warns; embedded attrs
  (`radius`,`start`,`gap`) parsed; bad numeric warns; `dock` flag set; only first
  radial honored.
- Layout: hub at canvas center; members share one ring (equal distance from hub
  center within tolerance); single member at `start`; radius override respected;
  group member keeps its members inside the frame.
- Geometry: `dock_anchor` returns a point on a polygon edge for a polygon hub;
  opposite spokes dock to different faces on a hexagon.
- Render/golden: `hub.fl`.
- Equivalence: sources without `radial` still match stack/layered goldens.
