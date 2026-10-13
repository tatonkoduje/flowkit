# Design — 0014 Timeline leading grid

## Problem, precisely

`layout()` computes `x_of(d)` over the domain `[lo, hi]` where `lo = range start`.
`plot_x0 = GUTTER`. The weekly grid runs from the Monday on/before `lo` (0013), so
when `lo` is itself mid-week the first gridline has `x < plot_x0` and is drawn in
the gutter; the plot's left strip has no gridline.

Example (current, `from 2026-05-21 grid week`):

```
plot_x0 = 190
May 18 gridline at x = 159.1  ← outside the plot (gutter)
marker (2026-05-21) at x = 190.0  ← flush with the plot edge
```

## Fix

Introduce a **domain start** `dom_lo`:

```python
dom_lo = lo
if timeline.grid == "week":
    dom_lo = lo - timedelta(days=lo.weekday())   # Monday on/before lo
```

Use `dom_lo` in the scaling:

```python
total_days = (hi - dom_lo).days or 1
def x_of(d):
    return plot_x0 + (d - dom_lo).days / total_days * plot_width
```

Now:

- the leading Monday is at `x = plot_x0` (the plot's left edge),
- the marker (`lo`) sits at `x > plot_x0` (a partial week in),
- the next gridlines fall at `plot_x0 + k*(week_px)`.

Gridline clamping is then automatic — the first gridline is exactly at
`plot_x0`, none to its left. No clamp code needed (the domain guarantees it), but
we still guard with `max(x, plot_x0)` for float safety.

`total_days` grows by `lo.weekday()` days (0–6), so bars/markers keep their true
relative spacing; only the visible window is a few days wider on the left.

## Ripple

- `_resolve_range` is unchanged (it still returns the user/derived `[lo, hi]`).
- Bars, milestones, markers, axis and grid all call `x_of`, so they shift
  consistently — the marker stays at its real date, now inside the plot.
- Without a weekly grid, `dom_lo == lo` → output identical to 0013.

## Determinism

`dom_lo` is fixed arithmetic from `lo.weekday()`; no randomness.

## Test strategy

- `grid week` + mid-week `from` ⇒ first gridline `x == plot_x0 (±0.5)`.
- The start marker `x > plot_x0`.
- `dom_lo` (a Monday) maps to `plot_x0`; a bar on the start date is right of the
  edge.
- No grid ⇒ domain start equals the range start (marker still at the edge; output
  unchanged versus 0013).
- Golden regenerated.
