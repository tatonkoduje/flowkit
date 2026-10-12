# Change 0002 — Shapes

- **Status:** draft
- **Type:** feature
- **Owner:** maintainers
- **Depends on:** [0001 walking-skeleton](../archive/0001-walking-skeleton/proposal.md)

## Why

0001 renders every node as a `card`. The visual language of an architecture
diagram depends on shape carrying meaning: a cylinder for a store, a hub for a
bus, a hexagon for a gateway. This change adds the shape vocabulary and makes
edges attach to the *real* shape border instead of a rectangle.

## What changes

- Add `shape=<shape>` to `node` (default `card`).
- Implement measurement for each shape: `card`, `db`, `hub`, `hex`, `pill`,
  `diamond`, `polyN` (regular polygon, N = 3…12).
- Per-shape **edge anchoring**: border intersection for rectangles, ray-cast for
  polygons, circle border for `hub`.
- Render each shape with the existing gradient + shadow treatment.

## Out of scope (later changes)

- `table` shape (needs `col:`/`row:` — change 0007)
- Groups, `layer`, `radial`
- Icons, edge labels/styles
- Two-line labels (`|`)

## Requirements touched

Folds into [`../../spec.md`](../../spec.md):
- Language: `node` gains `shape=`; shapes enumerated.
- Rendering: per-shape geometry and edge anchoring.

## Example + docs (required)

- New example `examples/shapes.fl` — every shape once.
- Rendered into `docs/gallery.md` (section "0002 — Shapes").
- `reference/language.md` — the `shape=` table and the anchoring note.

## Impact

- `src/flowlite/model.py` — add `shape` to `Node`.
- `src/flowlite/parser.py` — parse `shape=`.
- `src/flowlite/measure.py` — per-shape sizing.
- New `src/flowlite/shapes/geometry.py` — vertices, border/anchor math.
- `src/flowlite/render/svg.py` — draw shapes + use per-shape anchors.
- Tests: `tests/test_shapes.py`, update `tests/test_render.py` + golden.

## Open questions

- `diamond` label placement (single line centered) — acceptable for now?
- `polyN` label: centered, no icon yet (icons come later).
