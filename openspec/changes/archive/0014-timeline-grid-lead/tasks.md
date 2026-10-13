# Tasks — 0014 Timeline leading grid

## 1. Layout

- [x] 1.1 `layout/timeline.py`: when `grid == "week"`, extend the x-domain start
      to the Monday on/before the range start (`dom_lo`), and use it in `x_of` +
      `total_days`.
- [x] 1.2 Clamp gridline x to `plot_x0` for float safety.
- [x] 1.3 Tests: first gridline at the plot edge; marker right of the edge;
      leading Monday at `plot_x0`; no-grid domain unchanged.

## 2. Tests + golden

- [x] 2.1 Extend `tests/test_timeline.py`.
- [x] 2.2 Regenerate golden `tests/golden/timeline.svg`; graph goldens unchanged.

## 3. Example + docs (required)

- [x] 3.1 Re-commit `docs/img/timeline.svg` **and** `docs/img/timeline.png`.
- [x] 3.2 `reference/language.md` — note the leading-week grid.
- [x] 3.3 `openspec/spec.md` — update the grid-span scenario.

## 4. Close out

- [x] 4.1 Archive this change; add it to `changes/README.md`; CHANGELOG.

## Definition of done

- With `grid week`, the gray grid covers the area before the yellow start marker;
  the marker sits inside the plot; no gridlines in the gutter.
- Tests + ruff green; graph goldens unchanged.
- Gallery (svg+png), reference and spec updated; change archived.
