# Design — 0015 Timeline axis alignment & full leading week

## Current state

`layout()` (after 0014):

```python
dom_lo = lo - timedelta(days=lo.weekday()) if grid == "week" else lo
x_of(d) = plot_x0 + (d - dom_lo).days / total_days * plot_width
axis_ticks = _ticks(axis, lo, hi, x_of)     # ← uses `lo`, not `dom_lo`
grid_ticks = _ticks(grid, lo, hi, x_of, week_before=True)
```

`_ticks("month", lo, hi, …)` → `_month_starts(lo, hi)` starts at the 1st of `lo`'s
month = `2026-05-01`. With `dom_lo = 2026-05-18`, `2026-05-01 < dom_lo`, so its x
is negative-ish (`15.1`) — left of `plot_x0 = 190`.

## Fixes

### 1. Axis ticks bounded by the domain

Pass the **domain start** to the month-tick builder so the first month boundary is
the one **on or after `dom_lo`**:

```python
def _month_starts_in(dom_lo, hi):
    first = date(dom_lo.year, dom_lo.month, 1)
    if first < dom_lo:
        # advance one month
        first = _next_month(first)
    ... up to hi
```

Then `2026-06-01` is the first month tick (x inside the plot); `May 2026` is not
drawn outside. (If the domain contains a full month, its 1st still appears.)

### 2. Full leading week

```python
if grid == "week":
    monday = lo - timedelta(days=lo.weekday())
    dom_lo = monday - timedelta(days=7)   # the week before
else:
    dom_lo = lo
```

So `lo = 2026-05-21` ⇒ `dom_lo = 2026-05-11` (Monday), giving a complete empty
week (May 11→18) of grid before the marker, plus the partial week (May 18→21).

`total_days` grows accordingly; bars/markers keep true spacing.

## Interaction

- Grid ticks: `_ticks("week", dom_lo, hi, x_of, week_before=True)` — but now the
  grid should start at `dom_lo` itself (a Monday), so `week_before` can use
  `dom_lo` directly. Simplest: compute grid ticks from `dom_lo` (already a Monday)
  without further shifting.
- Month axis: computed from `dom_lo`.
- No weekly grid ⇒ `dom_lo = lo`, axis from `lo` (first month on/after lo) — this
  also fixes a latent off-by-one where a month label could precede the plot.

## Determinism

All arithmetic from fixed dates/weekday; no randomness.

## Test strategy

- No axis tick has `x < plot_x0` when `grid week` and a mid-week start.
- The domain start is a Monday exactly one week before the start-week Monday.
- A gridline exists a full week before the marker (e.g. `2026-05-11`).
- The marker is strictly inside the plot.
- Without a weekly grid, the first axis tick is inside the plot and the marker
  sits at `plot_x0` (range start) as before.
- Golden regenerated.
