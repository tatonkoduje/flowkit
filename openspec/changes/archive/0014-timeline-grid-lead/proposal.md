# Change 0014 — Timeline leading grid

- **Status:** draft
- **Type:** fix
- **Owner:** maintainers
- **Depends on:** [0013](../archive/0013-timeline-spacing/proposal.md)

## Why

In change 0013 the weekly gridlines were extended back to the Monday of the week
containing the range start, so a chart beginning mid-week would be gridded from
the left. But when the range **starts exactly on the start marker**
(`from 2026-05-21`), the plot's left edge *is* the marker x, and the leading
Monday (`2026-05-18`) falls **left of the plot** — it is drawn in the gutter,
outside the chart, and the strip between the plot edge and the first Monday
inside it has no gridline.

The result: the yellow "Start" marker sits flush against the plot's left edge and
there is **no gray gridline before it**. The intent (from the user) is the
opposite — the gray weekly grid should also cover the area **before** the start
line, so the leading partial week reads as part of the axis.

## What changes

When a weekly grid is active, the plot's **left edge is extended back to the
Monday on or before the range start**, and the range's start marker/item dates are
drawn at their true positions inside the plot. Concretely:

- The **x-domain** used for scaling starts at `grid_lo = Monday on/before lo`
  (only when `grid week` is set), so the leading partial week is *inside* the
  plot and gridded.
- The **yellow marker** then sits at its real date, a little to the right of the
  plot's left edge, with one or more gray gridlines to its left.
- Gridlines are **clamped to the plot area** (`x >= plot_x0`), so none are drawn
  in the gutter.
- Without a weekly grid, the range is unchanged (byte-identical to 0012/0013).

The date→x mapping and every bar/milestone/marker use the same extended domain,
so nothing else shifts relative to each other.

## Out of scope (later changes)

- Leading padding for `grid day` / `grid month` (only `week` today)
- Configurable lead padding (`lead=<px>`)
- Changing the marker colour/style

## Requirements touched

Folds into [`../../spec.md`](../../spec.md):
- Timeline: leading-week grid behaviour + gridlines clamped to the plot.

## Example + docs (required)

- `examples/timeline.fl` is unchanged; its golden **changes** because the plot now
  shows the leading week (the yellow line moves right, with a gray line before
  it). Regenerate `docs/img/timeline.svg` + `.png`.
- `reference/language.md` — one sentence on the leading-week grid.
- `openspec/spec.md` — update the "Gridlines span the whole plot" scenario.

## Impact

- `src/flowlite/layout/timeline.py` — extend the x-domain to the leading Monday
  when the grid is weekly; clamp gridline x to `plot_x0`.
- Tests: `tests/test_timeline.py` — leading gridline is inside the plot, the
  marker sits right of `plot_x0`, and the domain covers the leading week.
- Golden: `timeline.svg` regenerated.

## Open questions

- Should the lead also apply to `grid day`/`grid month`? Out of scope (only week).
- Should `from` be honoured exactly (no lead) when the user set it explicitly?
  Chosen: still add the lead, because the point is to grid before the start;
  documented.
