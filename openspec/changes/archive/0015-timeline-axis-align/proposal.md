# Change 0015 — Timeline axis alignment & full leading week

- **Status:** draft
- **Type:** fix
- **Owner:** maintainers
- **Depends on:** [0014](../archive/0014-timeline-grid-lead/proposal.md)

## Why

Two defects show up in the rendered timeline once the range starts mid-week with
`grid week`:

1. **The month axis is misaligned with the plot.** `_ticks("month", …)` builds
   tick dates from `_month_starts(lo, hi)`, i.e. the **1st of the month
   containing `lo`**, while the plot/date→x mapping uses `dom_lo` (the Monday of
   the start week from change 0014). When `lo = 2026-05-21`, the first month tick
   is `2026-05-01`, which lies *before* `dom_lo = 2026-05-18`; its x is
   `15.1` — **left of the plot's left edge (x = 190)**. The "May 2026" label is
   drawn outside the chart.

2. **Only a sliver of grid precedes the start marker.** With `dom_lo` = the
   Monday of the **same** week as `lo`, a Thursday start leaves a 3-day strip
   before the marker — barely one cell. The intent (from the user) is a clearly
   gridless-free **full week before** the line.

## What changes

- **Axis ticks use the domain start.** All axis/grid tick generation is
  computed relative to the extended x-domain, so no tick is drawn left of
  `plot_x0`. Concretely, the month axis starts from the first month boundary
  **on or after `dom_lo`**, and grid/axis share the same `dom_lo`/`x_of`.
- **A full leading week.** When `grid week` is active, the x-domain starts at the
  Monday of the week **before** the start week
  (`dom_lo = Monday(lo) - 7 days`), so the grid shows a complete empty week to
  the left of the start marker. Without a weekly grid, the domain starts at `lo`
  (unchanged).

Both are layout-only; the renderer is untouched.

## Out of scope (later changes)

- `grid day` / `grid month` leading padding (only `week` gets the extra week)
- Making the lead distance configurable (`lead=`)
- Cleaning the axis label at the very left edge (it sits at a week boundary now)

## Requirements touched

Folds into [`../../spec.md`](../../spec.md):
- Timeline: axis ticks bounded by the plot domain; one full leading week.

## Example + docs (required)

- `examples/timeline.fl` unchanged; golden regenerated (`May 2026` now inside the
  plot, and a full week of grid before the marker). Re-commit
  `docs/img/timeline.svg` + `.png`.
- `reference/language.md` — tweak the leading-week sentence (a full week).

## Impact

- `src/flowlite/layout/timeline.py` — compute the month axis from `dom_lo`;
  shift `dom_lo` a full week earlier for the weekly grid.
- Tests: `tests/test_timeline.py` — no axis tick left of `plot_x0`; the domain
  covers a full week before the marker; existing grid/marker tests updated.
- Golden: `timeline.svg` regenerated.

## Open questions

- Full week vs. "up to 2 weeks" lead: chosen one week (matches the weekly grid).
- Should the axis clamp ticks at `plot_x0` or shift the month start to the tick
  after? Chosen: start the month axis at the first month boundary inside the
  domain (no spurious left-edge label).
