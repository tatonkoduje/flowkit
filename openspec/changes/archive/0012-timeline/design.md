# Design — 0012 Timeline

## Model

```python
@dataclass(frozen=True)
class Marker:
    date: "date"
    label: str = ""

@dataclass(frozen=True)
class TimelineSection:
    title: str
    color: str = ""            # palette name or #hex; "" -> theme default
    kind: str = ""             # alias for color when using kinds

@dataclass(frozen=True)
class TimelineItem:
    label: str
    start: "date"
    end: "date"                # end == start for a single-day bar
    section: str = ""          # section title
    color: str = ""            # explicit override
    state: str = "normal"      # normal | done | active | planned
    note: str = ""
    milestone: bool = False    # True -> diamond at `start`

@dataclass(frozen=True)
class Timeline:
    title: str = ""
    subtitle: str = ""
    start: "date | None" = None      # explicit range
    end: "date | None" = None
    axis: str = "month"             # day | week | month
    grid: str = ""                  # "", day, week, month
    sections: tuple[TimelineSection, ...] = ()
    items: tuple[TimelineItem, ...] = ()
    markers: tuple[Marker, ...] = ()
```

`Diagram` gains `timeline: Timeline | None = None`. When set, the compiler uses
the timeline path and ignores nodes/edges.

## Parser

New instructions (recognized only as ordinary lines; each ends the previous
"current section" context except `bar`/`milestone`, which remember the most
recent `section` when `section=` is omitted):

```python
TIMELINE_RE = re.compile(r'^timeline\s+"([^"]*)"(?:\s+"([^"]*)")?(.*)$')
SECTION_RE  = re.compile(r'^section\s+"([^"]*)"(.*)$')
BAR_RE      = re.compile(r'^bar\s+"([^"]*)"\s+(\d{4}-\d{2}-\d{2})\s*->\s*(\d{4}-\d{2}-\d{2})(.*)$')
MILESTONE_RE= re.compile(r'^milestone\s+"([^"]*)"\s+(\d{4}-\d{2}-\d{2})(.*)$')
AXIS_RE     = re.compile(r'^axis\s+(\w+)(?:\s+grid\s+(\w+))?$')
MARKER_RE   = re.compile(r'^marker\s+(today|\d{4}-\d{2}-\d{2})(?:\s+"([^"]*)")?$')
```

`timeline` head also parses `from <date>` / `to <date>` from its tail.

Attribute scan on the tail: `section=`, `color=`, `state=`, `note=` (same helper
style as node attributes).

Validation (warnings, never fatal):
- timeline not declared → a `bar`/`section`/… instruction warns "outside a
  timeline" and is ignored.
- a `section=`/item referencing an unknown section title warns and attaches to a
  synthetic "(unassigned)" section rendered last.
- `end < start` warns and swaps.
- unknown `state`/`axis`/`grid` value warns and falls back to the default.
- a chart with `timeline` **and** nodes/edges warns "timeline wins".

## Colour resolution

`theme.timeline` provides the canvas + palette:

```json
"timeline": {
  "background": "#1D2125",
  "rowBand": "#242B33", "rowBandAlt": "#1F262E", "rowLabel": "#C7D2DD",
  "gridline": "#3A424D", "gridLabel": "#8A97A4",
  "axisLine": "#55636F", "axisLabel": "#C7D2DD",
  "barText": "#FFFFFF", "noteText": "#B6C2CF", "milestone": "#B6C2CF",
  "palette": {
    "slate": "#4C5966", "blue": "#1D7AFC", "teal": "#2898BD",
    "green": "#22A06B", "lime": "#6A9A23", "amber": "#F5CD47", "rose": "#E5484D"
  }
}
```

Resolution order for a bar fill:
1. item `color=` (palette name or `#hex`)
2. section `color=`
3. `state=` preset: `done` = the section colour dimmed to ~60%, `active` = the
   section colour boosted to full + a subtle glow, `planned` = transparent fill
   with a dashed section-colour outline, `normal` = the section colour.
4. theme default bar colour.

Milestones always use `timeline.milestone` unless overridden.

## Date → x mapping

```
day0 = range.start (ordinal)
dayN = range.end   (ordinal)
x(d) = gutter + (d.ordinal - day0) / (dayN - day0) * plot_width
```

- Range: explicit `from`/`to` if given; else `min(start)`…`max(end)` padded by one
  grid unit (or 3 days if no grid).
- `plot_width` is chosen so a week ≈ `WEEK_PX` (default 46 px) — this keeps bars
  legible; canvas width = gutter + plot_width + right margin.
- Row `y`: each section is a band of `SECTION_H`; items stack inside a band by
  `ROW_H`; a single-day bar is drawn at half `ROW_H`, vertically centred.

## Layout (`layout/timeline.py`)

Pure function `layout(timeline, theme) -> (placed, width, height)` where `placed`
carries, per item, `(x, y, w, h)` and per section `(y, h)`, plus tick positions
for the axis/grid. No randomness; no `now()`.

## Render (`render/timeline.py`)

Order (back to front):
1. background rect (theme `timeline.background`, or the theme gradient for
   consistency with graph diagrams — chosen: the gradient, matching FlowLite).
2. alternating section bands (rowBand/rowBandAlt) across the plot area.
3. gridlines + small grid labels (from `grid=unit`).
4. section titles in the gutter.
5. bars (rounded rects), milestone diamonds, bar labels (inside or right).
6. axis line + tick labels (`axis=unit`).
7. marker lines + labels (dashed, accent colour).
8. title / subtitle (top-left, same typography as graph renderer).

All text XML-escaped. Reuse `_defs` (shadows, gradients) so the look matches the
rest of FlowLite.

## Compiler dispatch

```python
if diagram.timeline is not None:
    placed, w, h = timeline_layout.layout(diagram.timeline, theme)
    return timeline_render.render(diagram.timeline, placed, theme, w, h)
# ... existing graph path (radial / layered / auto / stack)
```

## Determinism

- Ranges and tick dates are fixed arithmetic; no `now()`.
- Declaration order drives sections, items and markers.
- Float formatting identical to the graph renderer (`%.1f`).

## Test strategy

- **Parser:** timeline head (title/subtitle/from/to); section; bar (start→end);
  single-day bar; milestone; axis/grid; marker; `section=`/`color=`/`state=`/
  `note=`; each warning (outside a timeline, unknown section, end<start, unknown
  state/axis).
- **Date math:** `x(date)` is monotonic; range derivation from items; range
  padding; a single-day bar has zero width but non-zero min width.
- **Layout:** sections stack top→bottom in declaration order; items sit in their
  section band; milestones centred on their date.
- **Render:** title present; every section title, bar label and note present and
  escaped; a `done` bar differs in fill from an `active` bar; marker line drawn
  at the marker date's x.
- **Golden:** `timeline.fl`.
- **Equivalence:** graph examples (no `timeline`) are byte-identical.

## `timeline.fl` (the example this change ships)

A compact delivery timeline modelled on the Cassandra migration:

```fl
title "Delivery timeline" "phases, POCs and milestones"
timeline "Cassandra migration" from 2026-05-21 to 2026-10-31
axis month grid week
marker 2026-05-21 "Start 21 May 2026"

section "Discovery"        color=slate
section "Phase 0 — ADR"    color=blue
section "Epic"             color=slate
section "Phase 1"          color=teal
section "Phase 2"          color=green

bar "Idea / task created" 2026-05-21 -> 2026-05-21 section="Discovery" note="NTPSBK17-809"
bar "Research"            2026-05-29 -> 2026-06-11 section="Discovery"
milestone "Research resolved" 2026-07-21 section="Discovery"
bar "DevOps research"     2026-08-05 -> 2026-08-08 section="Discovery"

bar "Preparing ADR"       2026-06-07 -> 2026-07-29 section="Phase 0 — ADR" state=done
bar "POC — ZDM"           2026-07-06 -> 2026-07-14 section="Phase 0 — ADR" state=done
bar "POC — Spark"         2026-06-15 -> 2026-06-17 section="Phase 0 — ADR" state=done

milestone "Epic created"  2026-07-21 section="Epic" note="NTPSBK18-145"

bar "Setup Medusa"        2026-09-30 -> 2026-10-15 section="Phase 1" state=active
bar "Dashboards"          2026-10-07 -> 2026-10-15 section="Phase 1" state=active

bar "Migration script"    2026-09-21 -> 2026-09-22 section="Phase 2" state=planned
bar "Connect proxy"       2026-10-06 -> 2026-10-07 section="Phase 2" state=planned
```
