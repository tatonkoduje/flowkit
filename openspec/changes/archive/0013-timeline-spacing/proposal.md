# Change 0013 — Timeline spacing

- **Status:** draft
- **Type:** feature
- **Owner:** maintainers
- **Depends on:** [0012](../archive/0012-timeline/proposal.md)

## Why

A timeline's width is currently **fixed** by its date range: the layout hard-codes
`WEEK_PX = 46` (pixels per week), so a three-month plan and a three-year plan
render at the only width their span implies. On a wide slide or a document a
dense timeline is cramped (bar labels overflow), and on a narrow one a short
timeline is needlessly stretched. The author should be able to **stretch the x
axis** — make the gaps between weeks longer or shorter — and, when they want an
exact figure, pin the total width.

The range is already configurable (`from` / `to`). This change adds control over
**how spread out the days are**, which is the missing half.

## What changes

Add two optional attributes to the `timeline` header:

```fl
timeline "Title" [from <date>] [to <date>] [week=<px>] [width=<px>]
```

- `week=<px>` — **pixels per week** (the spacing between weeks on the x axis).
  Default stays `46`. `week=80` makes every week ~1.7× wider; `week=24` packs it
  tighter. This is the knob for "odstępy między tygodniami".
- `width=<px>` — **total plot width** in pixels, overriding `week=`. The axis is
  scaled so the range exactly fills `width`. Use it when you want a fixed figure.
- `width=` and `week=` are **mutually exclusive**; if both are given, `width=`
  wins and a warning notes that `week=` was ignored (or: warn and keep `week=` —
  see design). Either way one of them takes effect deterministically.
- Neither given → current behaviour (byte-identical for existing sources).

Additionally, **weekly gridlines shall span the whole plot width**, including the
part of the first week that falls **before** the range start. Today the first
gridline is the Monday *after* the start, so a chart beginning mid-week has an
empty strip on its left edge with no gridlines. The change aligns the first grid
line to the Monday on/before the range start (so the leading part-week is
gridded too), and the last line extends to cover the trailing part-week.

`from`/`to` (range) are unchanged and compose with both new attributes: range
picks *what* is shown, `week`/`width` pick *how wide* it is drawn.

## Out of scope (later changes)

- Per-section heights, zoom levels, horizontal scroll
- Denser axis tick intervals beyond day/week/month
- Non-linear time axes

## Requirements touched

Folds into [`../../spec.md`](../../spec.md):
- Timeline: `week=` / `width=` sizing attributes.

## Example + docs (required)

- **Extend** `examples/timeline.fl` in place to a wider, more readable chart
  (`week=72`), so the gallery shows the default example already benefiting — OR
  keep `timeline.fl` as-is and add `examples/timeline-wide.fl`. Decision (design):
  keep `timeline.fl` unchanged as the canonical example and add the spacing to it
  only if it still reads well; otherwise ship a golden-only progression. Chosen:
  **`timeline.fl` keeps default spacing; add nothing new** — instead document
  `week=`/`width=` in the reference and cover them in tests. (A dedicated example
  is optional; see design "Example decision".)

  Revised decision: **add `week=72` to `timeline.fl`** so the single example is the
  most readable version, regenerate its golden/gallery, and document both
  attributes. This keeps the "one example per change" rule while showing the win.
- Re-commit `docs/img/timeline.svg` and `docs/img/timeline.png`.
- `reference/language.md` — `week=` / `width=` rows in the `timeline` table.

## Impact

- `src/flowlite/model.py` — add `week: float | None` and `width: int | None` to
  `Timeline`.
- `src/flowlite/parser.py` — parse `week=`/`width=` on the `timeline` header;
  warn on non-numeric / non-positive; warn when both are given.
- `src/flowlite/layout/timeline.py` — use `timeline.week` (default `WEEK_PX`) for
  the plot width, or derive it from `timeline.width`.
- Tests: `tests/test_timeline.py` — week spacing, width override, warnings,
  defaults unchanged.
- Golden: `timeline.svg` regenerated for the new `week=72`.

## Open questions

- If both `week=` and `width=` are present: `width=` wins (chosen) vs warn+ignore.
- Should `week=` accept `0`/negative? No — warn and ignore (falls back to default).
- Units: pixels only (chosen) vs also allowing `week=2cm` style units (out of scope).
