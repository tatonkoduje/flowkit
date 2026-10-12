# Tasks — 0002 Shapes

## 1. Model + parser

- [ ] 1.1 `model.py`: add `shape: str = "card"` to `Node`.
- [ ] 1.2 `parser.py`: parse `shape=` (tolerate unknown shapes → warn + fall back to `card`).
- [ ] 1.3 Tests: `shape=` parsed; unknown shape warns and falls back.

## 2. Measurement

- [ ] 2.1 `measure.py`: per-shape sizing table (`card`, `db`, `hub`, `hex`, `pill`, `diamond`, `polyN`).
- [ ] 2.2 Parse `polyN` sides (3…12, clamp); store on the node.
- [ ] 2.3 Tests: sizes for each shape; `polyN` side parsing/clamping.

## 3. Geometry

- [ ] 3.1 `shapes/geometry.py`: `polygon_vertices(node)`.
- [ ] 3.2 `anchor(node, tx, ty)` — rect / circle / ray-cast polygon.
- [ ] 3.3 `vertical_anchor(node, bottom)` — uses real top/bottom (apothem for polygons).
- [ ] 3.4 Tests: vertices count/placement; anchors on the border.

## 4. Rendering

- [ ] 4.1 `shape_markup` dispatch in `render/svg.py`.
- [ ] 4.2 Draw `db` (cylinder + top ellipse), `hub` (circle + dashed ring),
      `hex`, `pill`, `diamond`, `polyN`.
- [ ] 4.3 Label placement per shape (left-aligned vs centered).
- [ ] 4.4 Edges use `geometry.vertical_anchor`.

## 5. Tests

- [ ] 5.1 `tests/test_shapes.py`.
- [ ] 5.2 Update `tests/golden/hello.svg` if needed.
- [ ] 5.3 New golden `tests/golden/shapes.svg`.

## 6. Example + docs (required)

- [ ] 6.1 `examples/shapes.fl` — every shape once.
- [ ] 6.2 Render to `docs/img/shapes.png` and embed in `docs/gallery.md`.
- [ ] 6.3 `reference/language.md` — `shape=` table + anchoring note.
- [ ] 6.4 `openspec/spec.md` — fold in the shape/anchoring requirements.

## 7. Close out

- [ ] 7.1 Move this change folder to `archive/`.
- [ ] 7.2 Mark 0002 done in `changes/README.md`.

## Definition of done

- `python3 -m flowlite examples/shapes.fl` renders all shapes with correct
  anchoring and no warnings.
- Tests + ruff green; golden + determinism green.
- Gallery, reference and spec updated.
