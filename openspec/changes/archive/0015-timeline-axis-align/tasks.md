# Tasks — 0015 Timeline axis alignment & full leading week

## 1. Layout

- [x] 1.1 Extend `dom_lo` a **full week earlier** (Monday of the previous week) when
      `grid == "week"`.
- [x] 1.2 Compute the month axis from `dom_lo` (first month boundary on/after it),
      so no tick is drawn left of `plot_x0`.
- [x] 1.3 Grid ticks derived from `dom_lo` directly (already a Monday).
- [x] 1.4 Tests: no axis tick left of the plot; a full week of grid before the
      marker; marker inside; no-grid unchanged.

## 2. Tests + golden

- [x] 2.1 Extend `tests/test_timeline.py`.
- [x] 2.2 Regenerate golden `tests/golden/timeline.svg`; graph goldens unchanged.

## 3. Example + docs (required)

- [x] 3.1 Re-commit `docs/img/timeline.svg` **and** `docs/img/timeline.png`.
- [x] 3.2 `reference/language.md` — leading-week wording (full week).
- [x] 3.3 `openspec/spec.md` — axis-bounded + full-leading-week scenario.

## 4. Close out

- [x] 4.1 Archive this change; add it to `changes/README.md`; CHANGELOG.

## Definition of done

- `May 2026` axis label is inside the plot; a full empty week of gray grid precedes
  the yellow start marker; no gridline/axis tick left of the plot.
- Tests + ruff green; graph goldens unchanged.
- Gallery (svg+png), reference and spec updated; change archived.
