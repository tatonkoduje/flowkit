# Change 0012 — Timeline (Gantt-style)

- **Status:** draft
- **Type:** feature
- **Owner:** maintainers
- **Depends on:** [0001](../archive/0001-walking-skeleton/proposal.md), [0002](../archive/0002-shapes/proposal.md)

## Why

Every FlowLite diagram so far is a **graph** (nodes + edges). A whole class of
real diagrams is not a graph at all: a **schedule**. Roadmaps, migration plans,
release trains and delivery timelines are drawn as horizontal **Gantt bars** on a
shared time axis — bars have a start, an end and a label; milestones are instants;
rows group work into phases; and each phase has a colour.

Today the team renders these with Mermaid Gantt plus a bespoke 300-line
post-processing script (`cassandra-migration-toolkit/docs/timeline/render_gantt.py`)
that patches the SVG after the fact because Mermaid cannot express fixed markers,
weekly gridlines, single-day bar heights, per-bar colours or a dark canvas.
FlowLite can make that a **first-class, dependency-free, deterministic** diagram
type — with a DSL that is far more readable than `task :crit, ph2p, 2026-10-06,
2026-10-07`.

The reference is the Cassandra-migration timeline
(`…/cassandra-migration-toolkit/docs/timeline/`): a dark Gantt with sections
(Discovery · Phase 0 · Epic · Phase 1 · Phase 2 · …), coloured phase bars,
milestone diamonds, a **`Start 21 May 2026`** marker line, weekly gridlines with
date labels, a month axis, and single-day bars drawn half-height.

## What changes at a glance

A new top-level instruction `timeline` (mutually exclusive with nodes/edges)
turns the source into a Gantt chart instead of a graph:

```fl
timeline "Cassandra Migration" from 2026-05-21 to 2026-10-31
axis month grid week
marker 2026-05-21 "Start 21 May 2026"

section "Discovery"        color=slate
section "Phase 0 — ADR"    color=blue
section "Phase 1"          color=teal

bar "Idea / task created"     2026-05-21 -> 2026-05-21  section="Discovery" note="NTPSBK17-809"
bar "Research"                2026-05-29 -> 2026-06-11  section="Discovery"
milestone "Research resolved" 2026-07-21                section="Discovery"

bar "Preparing ADR"           2026-06-07 -> 2026-07-29  section="Phase 0 — ADR" state=done
bar "POC — ZDM"               2026-07-06 -> 2026-07-14  section="Phase 0 — ADR" state=done
```

Reads top-to-bottom like the plan itself: **when the timeline runs**, which
**rows** exist and their **colours**, then each **bar / milestone** with its
**start → end** and a free-text **note**.

## What changes (specification)

### New diagram type

`timeline` is a **diagram-level directive**. A source that uses it compiles to a
Gantt SVG; a source that uses `node`/`edge` compiles to a graph SVG. Mixing the
two is a warning (the timeline wins; graph instructions are ignored) — the two
models do not compose.

### Range

```fl
timeline "Title" ["Subtitle"] [from <date>] [to <date>]
```

- `from`/`to` set the visible **range**. If omitted, the range SHALL be derived
  from the earliest start and latest end across all items (plus a small padding).
- Dates use ISO `YYYY-MM-DD`. (A later change may add `today`/relative dates.)

### Sections (rows)

```fl
section "Title" [color=<name|#hex>]
```

- Each `section` is one **row band** with a left-hand label; bars reference it by
  title with `section="…"`.
- `color=` names a timeline colour or a raw `#hex`; it fills the row band and is
  the default bar colour for that section.
- Sections render in declaration order; a section with no bars still renders (an
  empty row) — unlike Mermaid, which silently drops empty sections.

### Bars and milestones

```fl
bar <"label"> <start> -> <end> [section="…"] [color=…] [state=…] [note="…"]
milestone <"label"> <date>     [section="…"] [color=…] [note="…"]
```

- `bar` draws a rounded rectangle from `start` to `end`; a bar whose start equals
  its end is a **single day** and SHALL render at half height (so it stays visible
  on a long axis), matching the reference.
- `milestone` draws a **diamond** at one instant.
- `state=` ∈ `normal` | `done` | `active` | `planned` picks a default colour/alpha
  when no explicit `color=` is given: `done` muted, `active` accent (in-progress),
  `planned` dashed/ghosted outline. Mirrors the reference's run-state palette.
- `note="…"` is secondary text: drawn after the label (e.g. `NTPSBK17-809`,
  `work in progress`), smaller and dimmer.
- Labels that do not fit inside the bar SHALL be drawn to the right of the bar
  (the reference does exactly this).

### Axis, grid and markers

```fl
axis <unit> [grid <unit>]
marker <date> ["label"]
```

- `axis <unit>` ∈ `day` | `week` | `month` (default `month`) sets the tick labels
  along the bottom; the reference uses a **month** axis.
- `grid <unit>` (optional) draws vertical gridlines at that unit with a small date
  label. The reference uses **weekly (Monday)** gridlines.
- `marker <date> "text"` draws a vertical dashed marker line across the plot with
  a label above it (the reference's yellow `Start 21 May 2026`). Multiple markers
  allowed; a `marker today` special value (rendered at compile-input date only if
  supplied — never `now()`, to preserve determinism).

### Colours

Timeline colours extend the theme as **data**. A theme SHALL provide a
`timeline` block: `background`, `rowBand`, `rowBandAlt`, `rowLabel`, `gridline`,
`gridLabel`, `axisLine`, `axisLabel`, `barText`, `noteText`, `milestone`, and a
named **palette** (`slate`, `blue`, `teal`, `green`, `lime`, `amber`, `rose`, …).
`color=` accepts a palette name or a raw `#RRGGBB`. This satisfies "aesthetics as
data" — the dark look, the phase palette and the marker colour all come from the
theme file, not code.

### Rendering

- Left **gutter** column with section titles (vertical bands).
- Top **title** (and optional subtitle), matching the graph renderer's typography.
- A **month axis** along the bottom with larger date labels; **gridlines** behind
  the bars with small date labels near the base.
- Bars are `rx`-rounded, filled from the section/`state`/`color`, with the label
  centred inside (white) or to the right (muted) when it does not fit.
- Deterministic: bar order = declaration order; gridline dates = fixed arithmetic
  from the range; no `now()`, no randomness.

### Layout & measurement

Timeline reuses the existing **theme tokens**, **measurement** (char width for
labels) and **SVG primitives** (background gradient, shadows, edges/marker defs).
It adds one layout module `layout/timeline.py` that maps dates → x and rows → y,
and one render path `render/timeline.py` (or a branch in `render/svg.py`). The
compiler dispatches: if the model has a timeline, use the timeline renderer.

## Out of scope (later changes)

- Dependencies between bars (arrow "this after that") and critical-path shading
- Drag/click interactions, `link=` on bars, tooltips
- Zoom levels, day/week/month views in one figure, time zones / non-ISO formats
- Auto-today progress fill, percent-complete bars
- Combining timeline and graph in one figure

## Requirements touched

Folds into [`../../spec.md`](../../spec.md):
- A new `Timeline` requirement set (range, sections, bars, milestones, axis,
  grid, markers, colours, determinism) and a new top-level `timeline` directive.

## Example + docs (required)

- New example `examples/timeline.fl` — a compact **delivery timeline** in the
  spirit of the Cassandra migration (3–4 sections, a start marker, weekly grid, a
  few bars + milestones, mixed `done`/`active`/`planned`).
- Committed as `docs/img/timeline.svg` **and** `docs/img/timeline.png`; embedded
  in `docs/gallery.md`.
- `reference/language.md` — a `timeline` section documenting every keyword above.
- `docs/getting-started.md` — a one-paragraph "non-graph diagrams" note.

## Impact

- `src/flowlite/model.py` — add `Timeline`, `TimelineSection`, `TimelineItem`,
  `Marker`; add `timeline` to `Diagram`.
- `src/flowlite/parser.py` — parse `timeline`, `section`, `bar`, `milestone`,
  `axis`, `marker`; ISO date parsing + validation/warnings.
- `src/flowlite/measure.py` — timeline sizing (gutter/label widths → canvas).
- `src/flowlite/layout/timeline.py` — dates → x, rows → y (new).
- `src/flowlite/render/timeline.py` — the Gantt renderer (new).
- `src/flowlite/themes.py` + `themes/*.json` — a `timeline` colour block.
- `src/flowlite/compiler.py` — dispatch to the timeline renderer.
- Tests: `tests/test_timeline.py` (parser, date math, placement, render),
  golden `timeline.svg`.

## Design decisions (defaults chosen)

| Question | Choice |
|---|---|
| Syntax for a bar | `bar "label" START -> END` (verbose, self-documenting) |
| Sections | explicit `section` rows; **empty sections render** |
| Single-day bars | half height (reference behaviour) |
| Milestones | diamonds, size derived from row height |
| Axis default | `month`; `grid week` optional |
| Markers | vertical dashed line + label; `marker today` allowed as a literal **date**, never computed |
| Colours | theme `timeline` palette + raw `#hex`; `state=` presets |
| Range | explicit `from`/`to`, else derived from items |
| Mixing with graph | warning; timeline wins |

## Open questions

- Should `section` also accept a `height=` for tall phases, or stay uniform?
- Do we want `bar … note=` or a second `"…"` string (chosen: `note=`) to keep the
  primary label uncluttered?
- Range end: should `to` default to "the latest bar end + 1 week" or exactly the
  latest end (chosen: latest end, padded by one grid unit)?
