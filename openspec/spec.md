# FlowLite — Specification

> The living specification. Requirements use SHALL + concrete scenarios.
> Significant changes go through `openspec/changes/` before code.

The `.fl` source language: one instruction per line, `#` comments, double-quoted
strings.

## Language

### Requirement: Instruction-per-line source
The parser SHALL read a `.fl` file as one instruction per line, ignore blank lines
and `#` comments, and report unparseable lines as warnings without aborting.

#### Scenario: Blank lines and comments are ignored
- **WHEN** a file contains blank lines and lines starting with `#`
- **THEN** they contribute nothing to the diagram model

#### Scenario: Unparseable line warns and continues
- **WHEN** a line matches no known instruction
- **THEN** a warning is printed to stderr and the remaining file is parsed

### Requirement: Diagram header
The language SHALL support `title "main" "subtitle"` and `theme <name>`, with
defaults `"Diagram"` and `midnight` when omitted.

### Requirement: Nodes
The language SHALL support
`node <id> "label" [kind=] [shape=] [in=] [icon=] [link=]`, where `|`
in a label starts a smaller second line.

#### Scenario: Unknown shape falls back
- **WHEN** a node declares `shape=banana`
- **THEN** the shape falls back to `card` and a warning is emitted

### Requirement: Shapes
The language SHALL support shapes `card`, `db`, `hub`, `hex`, `pill`, `diamond`
and regular polygons `polyN` (N = 3…12). Nodes SHALL be measured to fit their
shape.

#### Scenario: Regular polygon
- **WHEN** a node declares `shape=poly8`
- **THEN** an octagon inscribed in the node's box is drawn

### Requirement: Per-shape edge anchoring
An edge SHALL attach to the border of the source and target shape facing the
other element: rectangle intersection for `card`/`db`/`pill`, the circle border
for `hub`, and ray-casting for `hex`/`diamond`/`polyN`. Two vertically stacked
items SHALL connect bottom-center to top-center.

#### Scenario: Stacked shapes
- **WHEN** two shapes are stacked vertically and connected
- **THEN** the edge meets the bottom of the upper shape and the top of the lower one

### Requirement: Groups
The language SHALL support `group <id> "title" [kind=]` creating a translucent
background frame; nodes join with `in=<id>`. Members SHALL be laid out in a grid
inside the frame, and an edge MAY target a group id.

#### Scenario: Node joins a group
- **WHEN** a node declares `in=core` and a group `core` exists
- **THEN** the node is drawn inside the group's frame

#### Scenario: Unknown group warns and detaches
- **WHEN** a node declares `in=ghost` and no group `ghost` exists
- **THEN** the node is placed standalone and a warning is emitted

#### Scenario: Edge targets a group
- **WHEN** an edge references a group id
- **THEN** the edge anchors to the frame border

### Requirement: Group rendering
Group frames SHALL be drawn under the nodes and edges, with a translucent
kind-colored fill, a dashed border and a title label inside the frame.

### Requirement: Tables
The language SHALL support `table <id> "title" [kind=]` with `col:` and `row:`
lines; cells are separated by `|` and trimmed. The `col:` line SHALL be the header
row. A table SHALL be a top-level item, measured from its cells and positioned by
the active layout engine, and an edge MAY target a table id (anchoring to its
border).

#### Scenario: Header and rows render
- **WHEN** a table declares `col: a | b` and `row: 1 | 2`
- **THEN** a header row with cells `a`/`b` and a data row `1`/`2` are drawn

#### Scenario: Shorter row leaves blanks
- **WHEN** a row has fewer cells than the header
- **THEN** the missing cells render blank

#### Scenario: Over-long row warns
- **WHEN** a row has more cells than the header
- **THEN** the extra cells are dropped and a warning is emitted

#### Scenario: Cell line without a table warns
- **WHEN** a `col:`/`row:` line appears before any `table` (or after the table
  was closed by another instruction)
- **THEN** the line is ignored and a warning is emitted

#### Scenario: Edge targets a table
- **WHEN** an edge references a table id
- **THEN** the edge anchors to the table border

### Requirement: Edges
The language SHALL support
`edge <from> -> <to> ["label"] [style=] [arrow=] [curve=]`, attaching to the
border of the target facing the other element.

#### Scenario: Edge style and arrow variants
- **WHEN** an edge declares `style=dashed`, `style=bold`, `arrow=dot`,
  `arrow=none` or `curve=straight`
- **THEN** the corresponding stroke, head or curve is rendered

#### Scenario: Edge label
- **WHEN** an edge declares a quoted label
- **THEN** the label is drawn on a pill at the edge midpoint

#### Scenario: Unknown edge value
- **WHEN** an edge declares `style=wavy`
- **THEN** the style falls back to `normal` and a warning is emitted

### Requirement: Layered layout
The language SHALL support `layer <n>: ids` assigning top-level items (standalone
nodes and groups) to ordered columns, laid out left-to-right in ascending `<n>`
order and centered vertically. Items not assigned to a layer SHALL be placed in a
trailing column in declaration order. Without any `layer` instruction the default
vertical stack SHALL be used unchanged.

#### Scenario: Columns render left-to-right
- **WHEN** a source declares `layer 1: a` and `layer 2: b`
- **THEN** `a` is placed in the left column and `b` in the right column

#### Scenario: Unassigned items trail
- **WHEN** a node is named in no layer
- **THEN** it is placed in a trailing column after all numbered layers

#### Scenario: Unknown layer id warns
- **WHEN** a layer names an id that matches no node or group
- **THEN** the id is ignored and a warning is emitted

### Requirement: Radial layout
The language SHALL support a `radial hub=<id> [radius=] [start=] [dock] [gap=]`
instruction that places the hub node at the center and every other top-level item
(standalone node or group) evenly on a ring around it, in declaration order,
clockwise from `start` (default `-90`, i.e. 12 o'clock). Without `radius=`, the
ring SHALL be sized from the hub extent, the largest member extent and `gap`.
When both `radial` and `layer` are declared, `radial` SHALL take precedence.

#### Scenario: Hub is centered
- **WHEN** a source declares `radial hub=a`
- **THEN** node `a` is placed at the canvas center and the other items on a ring

#### Scenario: Polygon-face docking
- **WHEN** `radial hub=a dock` is declared and `a` is a polygon (`hex`, `diamond`,
  `polyN`)
- **THEN** each spoke leaves from the polygon face facing its member, and two
  spokes in opposite directions dock to different faces

#### Scenario: Unknown hub falls back
- **WHEN** `radial hub=<id>` names no node
- **THEN** the instruction is ignored, a warning is emitted, and the default
  layout is used

#### Scenario: Dock needs a polygon hub
- **WHEN** `dock` is requested on a non-polygon hub
- **THEN** it is ignored, a warning is emitted, and spokes ray-cast from center

### Requirement: Auto layout
The language SHALL support a `layout auto` directive that derives the columns
from the **edges** (directed, Sugiyama-style), placing top-level items
left-to-right in edge order. Layering SHALL use longest paths from the sources
and SHALL be cycle-safe (back edges dropped). It SHALL be opt-in; without it the
default stack is used. An explicit `layer` or `radial` SHALL override it.

#### Scenario: Columns come from edges
- **WHEN** a source declares `layout auto` with `edge a -> b` and `edge b -> c`
- **THEN** `a`, `b` and `c` are placed in successive left-to-right columns

#### Scenario: Cycles are safe
- **WHEN** the edges contain a cycle
- **THEN** layout still terminates and every node is placed

#### Scenario: Explicit layout wins
- **WHEN** `layout auto` coexists with a `layer` instruction
- **THEN** the explicit layers are used and a warning notes auto-layout was ignored

### Requirement: Explicit layout overrides
Placement instructions (`layer`, `radial`) SHALL place named top-level items
explicitly; unassigned items SHALL fall back to the default stack. See
[Layered layout](#requirement-layered-layout) and
[Radial layout](#requirement-radial-layout).

### Requirement: Timeline
The language SHALL support a `timeline` diagram type rendering a Gantt chart:
`timeline "title" ["subtitle"] [from <date>] [to <date>] [week=<px>] [width=<px>]`,
`section "title" [color=]`, `bar "label" <start> -> <end> [section=] [color=]
[state=] [note=]`, `milestone "label" <date> [section=] [color=] [note=]`,
`axis <unit> [grid <unit>]` and `marker <date> ["label"]`, with ISO
`YYYY-MM-DD` dates. A source that uses `timeline` SHALL ignore graph
instructions (with a warning).

#### Scenario: Range and axis
- **WHEN** a timeline declares `from`/`to` and `axis month grid week`
- **THEN** the plot spans that range with monthly tick labels and weekly gridlines

#### Scenario: Configurable axis width
- **WHEN** a timeline declares `week=<px>` (or `width=<px>`)
- **THEN** the plot is drawn at that pixels-per-week (or exact width); the range is
  unchanged; if both are given `width=` wins with a warning

#### Scenario: Gridlines span the whole plot
- **WHEN** `grid week` is set
- **THEN** the plot starts one full week before the range start (the previous
  Monday), so a complete empty week of gray gridlines precedes the start marker
  (which sits well inside the plot), and no axis label is drawn left of the plot

#### Scenario: Axis is bounded by the plot
- **WHEN** the range starts mid-month with `grid week`
- **THEN** the first month tick is on or after the plot's left edge (no label
  outside the chart)

#### Scenario: Bars carry start, end, colour and note
- **WHEN** a `bar` declares a `section=`, `color=`, `state=` or `note=`
- **THEN** the bar is drawn in that row with the resolved colour and its label/note

#### Scenario: Single-day bar
- **WHEN** a bar's start equals its end
- **THEN** it renders as a half-height bar with a minimum visible width

#### Scenario: Milestone
- **WHEN** a source declares a `milestone`
- **THEN** a diamond is drawn at that date

#### Scenario: Marker
- **WHEN** a source declares `marker <date> "text"`
- **THEN** a vertical dashed marker line with the label is drawn at that date

#### Scenario: Timeline wins over graph instructions
- **WHEN** a source declares `timeline` and also `node`/`edge`
- **THEN** the timeline is rendered and the graph instructions are ignored with a
  warning

#### Scenario: Timeline validation warns
- **WHEN** a timeline instruction appears before any `timeline`, references an
  unknown section, has `end < start`, or an unknown axis/grid/state/week/width
- **THEN** a warning is emitted and the default/swap applies

## Rendering

### Requirement: Vector-first output
The compiler SHALL always produce a standalone SVG with a `viewBox`, and SHALL
optionally export PNG (best-effort).

#### Scenario: PNG is best-effort
- **WHEN** `--png` is requested and no converter is installed
- **THEN** the SVG is still written and a clear message is printed to stderr

#### Scenario: First available converter is used
- **WHEN** `--png` is requested and a supported converter is installed
- **THEN** a PNG is written next to the SVG and the converter name is reported

#### Scenario: PNG sizing
- **WHEN** `--png-scale` or `--png-width` is given with `--png`
- **THEN** the PNG is scaled by the factor (default `2`) or rendered at the width

#### Scenario: Conflicting sizing options
- **WHEN** `--png-scale` and `--png-width` are given together
- **THEN** the command exits non-zero without writing output

### Requirement: Presentation-quality defaults
Renderers SHALL produce gradient-filled cards, a soft drop shadow, rounded corners
and vector icons with no additional configuration.

### Requirement: Deterministic rendering
The renderer SHALL be a pure function of the model and theme, producing
byte-identical SVG for identical input.

#### Scenario: Recompiling an unchanged source
- **WHEN** the same source is compiled twice
- **THEN** the two SVG files are byte-for-byte identical

### Requirement: Safe text
All user-provided text SHALL be XML-escaped before being written into SVG.

### Requirement: Icons are data
The language SHALL support an `icon=<name>` node attribute drawing a vector icon
inside the node, tinted to match the label. The icon set SHALL be vendored as a
data file (a curated lucide subset, ISC) and SHALL NOT introduce a runtime
dependency. A node without `icon=` SHALL render unchanged.

#### Scenario: Icon drawn in the node
- **WHEN** a node declares `icon=database`
- **THEN** the database glyph is drawn inside the node, tinted like the label

#### Scenario: Unknown icon warns
- **WHEN** a node declares `icon=<name>` that is not in the vendored set
- **THEN** the icon is ignored and a warning is emitted

### Requirement: Interactive links
The language SHALL support a `link=<url>` node attribute that wraps the node
(shape and label) in an SVG hyperlink, opening the target in a new tab. The URL
SHALL be XML-escaped. A node without `link=` SHALL render unchanged.

#### Scenario: Node becomes a hyperlink
- **WHEN** a node declares `link=<url>`
- **THEN** the node's shape and label are wrapped in an `<a href>` for `url`

#### Scenario: Empty link warns
- **WHEN** a node declares an empty `link=`
- **THEN** the link is ignored and a warning is emitted

## Theming

### Requirement: Themes are data
A theme SHALL be defined in a data file under `themes/` and selected by name.
Render logic SHALL NOT hard-code theme colors.

### Requirement: Theme contents
A theme SHALL define canvas background, title/subtitle colors, edge and
edge-label colors, a palette for every supported `kind`, and the design tokens
(paddings, gaps, radii, shadow, font stack).

### Requirement: Unknown theme fails clearly
Selecting an unknown theme SHALL fail with a message naming the unknown theme.

## CLI

### Requirement: Module entry point
FlowLite SHALL be runnable as `python3 -m flowlite <input.fl>`.

#### Scenario: Default output
- **WHEN** `python3 -m flowlite diagram.fl` is run
- **THEN** `build/diagram.svg` is written

### Requirement: Options and exit codes
The CLI SHALL accept `-o/--output PATH` and `--png`, exit `0` on success and
non-zero on failure, and provide `--help`.
