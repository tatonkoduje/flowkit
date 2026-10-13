# Design — 0013 Timeline spacing

## Model

```python
@dataclass(frozen=True)
class Timeline:
    ...
    week: float | None = None    # pixels per week; None -> layout default (46)
    width: int | None = None     # total plot width; overrides `week`
```

Both default to `None` → existing sources produce byte-identical SVG.

## Parser

Extend the `timeline` head parse. Two new attribute regexes on the head tail:

```python
TL_WEEK_RE  = re.compile(r"\bweek=(\d+(?:\.\d+)?)")
TL_WIDTH_RE = re.compile(r"\bwidth=(\d+)")
```

- `week=<n>` with `n > 0` → `week = float(n)`.
- `width=<n>` with `n > 0` → `width = int(n)` (px).
- non-numeric or `<= 0` → warn (`week must be a positive number, ignored`) and
  leave `None`.
- both present → warn (`width overrides week`) and clear `week` (so `width` wins).
- Neither → both `None`.

The regex requires a number, so `week=abc` won't match; detect it separately to
warn (same pattern as radial's `RADIAL_BAD_NUM_RE`). `week=` with a value like
`week=0` matches but fails the `> 0` check → warn.

## Layout

`layout/timeline.py` currently computes:

```python
plot_width = max(240.0, total_days / 7.0 * WEEK_PX)
```

New:

```python
if timeline.width is not None:
    plot_width = float(timeline.width)
else:
    week_px = timeline.week if timeline.week is not None else WEEK_PX
    plot_width = max(240.0, total_days / 7.0 * week_px)
```

Everything downstream (date→x, ticks, bars, markers) already derives from
`plot_width`, so no other change is needed — the whole chart scales with the axis.

Determinism preserved: both values are fixed numbers from the source.

## Grid continuity (gridlines before the start)

`_ticks("week", …)` currently begins at `_first_monday(lo)` — the Monday on or
**after** the range start. If the range starts mid-week, the leading days have no
gridline (an empty strip on the left).

Change: the weekly grid starts at the Monday on or **before** `lo`, so the first
(partial) week is gridded, and the loop runs while `day <= hi` — extending the
last line to wherever the trailing part-week ends. The first grid label may sit
slightly left of `plot_x0`; clamp drawing to the plot (`x >= plot_x0`), or keep it
and let the section band clip visually — chosen: **draw it** so the leading
part-week is visibly gridded, matching the user's request. Axis ticks (the
bottom month labels) are unchanged; only the grid unit is affected.

Implement as: `first = lo - timedelta(days=lo.weekday() + (0))` i.e. the Monday of
the week containing `lo` (`lo.weekday()` days back). Emit that day plus every 7
days up to `hi`.

## Interaction with the range

- `from`/`to` set `total_days` (as today).
- `week=` sets px/week ⇒ `plot_width = weeks * week_px`.
- `width=` sets `plot_width` directly ⇒ effective px/week = `width / weeks`.

So a user can express either "spacing between weeks" (`week=`) or "exact total
width" (`width=`), and the range still decides the span.

## Example decision

`examples/timeline.fl` gains `week=72` on its `timeline` header — the single
canonical example becomes visibly more readable (bar labels fit inside bars),
which is the point of the change. Its golden and gallery images are regenerated.
The reference documents both `week=` and `width=` with a `width=1600` example.

## Test strategy

- **Parser:** `week=72` parsed; `width=1600` parsed; `week=0` warns + ignored;
  `week=abc` warns + ignored; both → `width` wins + warning; defaults `None`.
- **Layout:** a larger `week=` yields a larger `width`; `width=` yields exactly
  that plot width; dates still land within `[plot_x0, plot_x1]`; growth is
  proportional (double `week` ⇒ ~double plot width).
- **Equivalence:** a timeline with neither attribute renders identically to 0012
  (byte-for-byte).
- **Golden:** regenerated `timeline.svg` (now `week=72`).
