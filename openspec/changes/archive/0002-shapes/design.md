# Design — 0002 Shapes

## Shape model

`Node.shape` is a string. Two families:

- **Named shapes**: `card`, `db`, `hub`, `hex`, `pill`, `diamond`.
- **Regular polygons**: `polyN`, N = 3…12 (e.g. `poly5`, `poly6`, `poly8`).

Sizing is centralized in `measure.py`; geometry (vertices + anchors) lives in a
new `shapes/geometry.py` so the renderer and the edge logic share one source of
truth for where a shape's border is.

## Measurement

| Shape | Box | Notes |
|---|---|---|
| `card` | w from label, h = `nodeHeight` | rounded rect |
| `db` | like card, taller (h ≈ 78) | cylinder |
| `hub` | square, `d = max(112, text_w + 46)` | circle |
| `hex` | wider (extra for the cut corners) | hexagon |
| `pill` | h ≈ 52, fully rounded | stadium |
| `diamond` | w ≈ text_w·1.9 + 40, h ≈ 96 | rhombus |
| `polyN` | square, `d = max(130, text_w + 60)` | regular polygon |

Scale is **not** in scope here (that is a later concern); all shapes render at
scale 1.

## Geometry (`shapes/geometry.py`)

- `polygon_vertices(node)` — vertices of a regular `polyN`, inscribed in the box;
  even N gets a flat top (offset −90° vs −90°+π/N).
- `anchor(node, tx, ty)` — border point facing `(tx, ty)`:
  - `card`, `db`, `pill` → rectangle border intersection.
  - `hub` → point on the circle of radius `w/2`.
  - `hex`, `diamond`, `polyN` → ray-cast against the real polygon edges.
- `vertical_anchor(node, bottom)` — bottom-center / top-center, using the real
  top/bottom for polygons (apothem) so stacked edges touch the shape.

## Rendering

Extend `render/svg.py` with a `shape_markup(node, theme)` dispatch. Each shape
draws its body (gradient + shadow + subtle white stroke) and then the label:

- `card`/`pill`/`hex`/`db` → left-aligned label with padding.
- `hub`/`diamond`/`polyN` → centered label.

Edges switch from the hard-coded bottom/top rectangle anchors to
`geometry.vertical_anchor`, so they meet the actual shape.

## Determinism

Geometry is pure math on the model; no randomness or ordering hazards. Polygon
vertices are computed in a fixed index order.

## Test strategy

- `test_shapes.py`: sizing per shape; `polygon_vertices` count and radius;
  anchors lie on the border (point-in-shape / distance checks).
- `test_render.py`: each shape emits its distinctive element (e.g. `<ellipse>`
  for `db` top, `<circle>` for `hub`, `<polygon>` for `hex`/`diamond`/`polyN`);
  golden updated for `hello.fl` (now uses `store`/`gateway` kinds but still
  `card`); new golden for `shapes.fl`.
- Determinism: compile `shapes.fl` twice → equal.
