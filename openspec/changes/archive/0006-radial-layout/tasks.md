# Tasks — 0006 Radial layout

## 1. Model

- [x] 1.1 `model.py`: add `Radial`; add `radial: Radial | None` to `Diagram`.

## 2. Parser

- [x] 2.1 Parse `radial hub=<id> [radius=] [start=] [dock] [gap=]`.
- [x] 2.2 Warn on missing/unknown hub (drop radial); warn on bad numeric attrs
      (ignore attr); set `dock` flag; only first `radial` honored.
- [x] 2.3 Tests: parse head + attrs; missing hub warns; bad numeric warns.

## 3. Geometry

- [x] 3.1 `shapes/geometry.py`: `dock_anchor(node, tx, ty)` — polygon-face anchor,
      deterministic face choice; ray-cast fallback for non-polygons.
- [x] 3.2 Correct `hex` geometry to match the drawn flat-topped hexagon
      (`hex_vertices` shared with the renderer); regenerate the `shapes.svg`
      golden (0002); keep all other goldens unchanged.

## 4. Layout

- [x] 4.1 `layout/radial.py`: hub centered; members evenly on a ring.
- [x] 4.2 Radius override + `gap` default; `start` angle; clockwise order.
- [x] 4.3 Group member: place frame on ring, members via shared grid helper.
- [x] 4.4 Tests: hub centered; ring equidistant; single member at `start`;
      radius respected; group member contained.

## 5. Renderer

- [x] 5.1 `render/svg.py`: for a radial+dock diagram, anchor hub-incident edges
      with `dock_anchor` (polygon hub); other edges unchanged.

## 6. Compiler

- [x] 6.1 Choose engine: radial > layered > stack.

## 7. Tests

- [x] 7.1 `tests/test_radial.py`.
- [x] 7.2 New golden `tests/golden/hub.svg`; existing goldens unchanged.

## 8. Example + docs (required)

- [x] 8.1 `examples/hub.fl` — hexagon bus with docked producers/consumers.
- [x] 8.2 Commit `docs/img/hub.svg` **and** `docs/img/hub.png`; embed in gallery.
- [x] 8.3 `reference/language.md` — `radial` section; drop it from "planned".
- [x] 8.4 `openspec/spec.md` — fold in radial requirements.

## 9. Close out

- [x] 9.1 Archive this change; mark 0006 done in `changes/README.md`.

## Definition of done

- `hub.fl` renders a hub with spokes on a ring; polygon hub docks to faces;
  no warnings on the example.
- Tests + ruff green; golden + determinism green; stack/layered output unchanged.
- Gallery (svg+png), reference and spec updated; change archived.
