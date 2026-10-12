# FlowLite — Language reference

> **Status:** early. This reference describes what the compiler supports **today**
> and marks what is planned. Requirements live in
> [`openspec/spec.md`](../openspec/spec.md).

A `.fl` file contains **one instruction per line**. Blank lines are ignored.
`#` starts a comment. Strings use double quotes `"`.

---

## `title` — diagram header

```fl
title "Main title" "optional subtitle"
```

| Parameter | Required | Default | Description |
|---|---|---|---|
| 1 | no | `"Diagram"` | main title |
| 2 | no | *(empty)* | subtitle |

## `theme` — color scheme

```fl
theme midnight
```

Supported today: `midnight` (default, dark) · `light`.
Themes are data files in [`themes/`](../themes/); see
[Recommendations](RECOMMENDATIONS.md) for the direction.

## `node` — a shape

```fl
node <id> "Label" kind=<kind> shape=<shape>
```

| Attribute | Required | Default | Description |
|---|---|---|---|
| `id` | yes | — | unique identifier, used by `edge` |
| `"label"` | yes | — | display text |
| `kind=` | no | `default` | color palette |
| `shape=` | no | `card` | geometry (see below) |
| `in=` | no | *(none)* | id of the `group` this node belongs to |
| `icon=` | no | *(none)* | name of a vendored icon (see below) |
| `link=` | no | *(none)* | URL the whole node links to (see below) |

### Shapes

| `shape=` | Geometry | Typical use |
|---|---|---|
| `card` *(default)* | rounded rectangle | services, generic components |
| `db` | cylinder | databases, stores |
| `hub` | circle + dashed glow ring | event buses, integration hubs |
| `hex` | hexagon | gateways, external systems |
| `pill` | stadium (fully rounded) | workers, schedulers, brokers |
| `diamond` | rhombus | decisions |
| `polyN` | regular polygon, N = 3…12 (`poly5`, `poly6`, `poly8`, `poly10`); even N gets a flat top | cores and heroes |

Unknown shapes fall back to `card` with a warning.

An edge attaches to the **real border** of the shape facing the other node:
rectangle intersection for `card`/`db`/`pill`, the circle border for `hub`, and
ray-casting for `hex`/`diamond`/`polyN`. Two stacked items connect
bottom-center to top-center.

> **Tolerated but ignored today:** other attributes such as `scale=` — FlowLite
> parses the node and ignores the rest.

### Interactive links

`link=<url>` makes the **whole node** — its shape and label — a hyperlink in the
SVG. Relative paths, `#anchors` and `https://…` URLs all work; the URL is copied
verbatim (and XML-escaped). Links open in a new tab
(`target="_blank" rel="noopener noreferrer"`).

```fl
node pipeline "Layered layout" kind=service icon=layers link=../../examples/pipeline.fl
```

A node without `link=` renders exactly as before. An empty `link=` warns and is
ignored. Only **nodes** are linkable (not groups, tables or edges).

### Icons

`icon=<name>` draws a small vector icon inside the node, tinted white like the
label. The set is **vendored as data** in [`icons/lucide.json`](../icons/lucide.json)
(a curated [lucide](https://lucide.dev) subset, ISC) — no runtime dependency.

Vendored names:

| Icon | Typical use | Icon | Typical use |
|---|---|---|---|
| `database` | stores | `credit-card` | payments |
| `server` | services | `shopping-cart` | orders |
| `cloud` | external systems | `activity` | analytics, metrics |
| `globe` | web, internet | `bell` | notifications |
| `network` | gateways, buses | `file-text` | documents |
| `git-branch` | decisions, pipelines | `box` | generic container |
| `user` / `users` | users / user groups | `cpu` | compute |
| `shield` | security | `hard-drive` | storage |
| `lock` | auth | `zap` | queues, fast paths |
| `key` | keys | `layers` | stacks |
| `message-square` | events, messages | | |

An unknown icon name warns and is ignored (the node renders without an icon).
Icons are additive: a node without `icon=` renders exactly as before.

### Kinds (color palettes)

`source` `queue` `service` `store` `consumer` `gateway` `app` `web` `mobile`
`tablet` `default`.

## `group` — a translucent frame

```fl
group <id> "Title" kind=<kind>
```

| Attribute | Required | Default | Description |
|---|---|---|---|
| `id` | yes | — | unique identifier, used by `node ... in=` and `edge` |
| `"title"` | yes | — | label shown at the top-left inside the frame |
| `kind=` | no | `default` | color palette of the frame border and fill |

A group draws a **translucent, dashed frame** under the nodes. Nodes join it
with `in=<group-id>`; members are laid out automatically in a centered grid
inside the frame. A node whose `in=` names an unknown group is detached (placed
standalone) with a warning.

An `edge` may reference a **group id** directly; it anchors to the frame border,
so a whole group can be a source or target.

```fl
group core "Core services" kind=service
node gw   "API Gateway" kind=gateway in=core
node slip "Betslip"     kind=service in=core

group data "Data" kind=store
node pg "PostgreSQL" kind=store shape=db in=data

edge core -> data "persist" style=dashed
```

Empty groups fall back to a minimum frame size. Polygonal group frames
(`shape=`) and nested groups are **not** supported yet.

## `edge` — a connector

```fl
edge <from> -> <to> "label" style=<style> arrow=<arrow> curve=<curve>
```

| Attribute | Required | Default | Description |
|---|---|---|---|
| `from` / `to` | yes | — | node **or group** ids |
| `"label"` | no | *(none)* | text on a pill at the edge midpoint |
| `style=` | no | `normal` | `normal` · `dashed` · `bold` |
| `arrow=` | no | `normal` | `normal` (triangle) · `dot` · `none` |
| `curve=` | no | `bezier` | `bezier` (smooth) · `straight` (line) |

Attributes may appear in any order after the label. Unknown values fall back to
the default with a warning. Edges referencing unknown ids are skipped.

When two nodes are stacked vertically, the edge connects their bottom/top centers;
otherwise it attaches to the real border of each shape (see [Shapes](#shapes)).

## `layer` — ordered columns

```fl
layer <n>: <id> [<id> ...]
```

| Parameter | Required | Default | Description |
|---|---|---|---|
| `<n>` | yes | — | positive integer ordering columns left-to-right |
| `<id> ...` | yes | — | space-separated node or group ids |

Assigns **top-level items** (standalone nodes and groups) to ordered columns.
Columns are laid out left-to-right in ascending `<n>` order and each is centered
vertically. Items not named in any layer fall into a **trailing column** in
declaration order.

```fl
layer 1: web mob
layer 2: gw
layer 3: slip offer
layer 4: pg cass
```

- A node id that matches nothing warns and is ignored.
- A node listed in two layers stays in the **first** one; the later entry warns.
- A **group id** may be used to place the whole frame in a column.
- Without any `layer`, the default vertical stack is used.

## `radial` — hub and spokes

```fl
radial hub=<id> [radius=<r>] [start=<deg>] [dock] [gap=<g>]
```

| Parameter | Required | Default | Description |
|---|---|---|---|
| `hub=` | yes | — | node id placed at the center |
| `radius=` | no | derived | ring radius in pixels |
| `start=` | no | `-90` | angle of the first spoke (degrees; `-90` = 12 o'clock) |
| `dock` | no | off | dock spokes to a polygon hub's faces |
| `gap=` | no | `70` | clearance between the hub and the ring |

Places the `hub=` node at the center and every other **top-level item**
(standalone nodes and groups) evenly on a ring around it, clockwise from
`start`. Without `radius=`, the ring is sized from the hub and largest member
plus `gap`.

```fl
radial hub=bus radius=300 start=-90 dock
```

- A missing or unknown `hub=` warns and the diagram falls back to the stack.
- A non-numeric `radius`/`start`/`gap` warns and that attribute is ignored.
- `dock` on a non-polygon hub warns and is ignored (the spoke ray-casts instead).
- A **group id** is not a valid hub; groups may be ring members.
- When both `radial` and `layer` are present, `radial` wins.

---

## `table` — a titled grid

```fl
table <id> "Title" [kind=<kind>]
col: <cell> | <cell> | ...
row: <cell> | <cell> | ...
```

| Parameter | Required | Default | Description |
|---|---|---|---|
| `id` | yes | — | unique identifier, used by `edge` |
| `"title"` | yes | — | header shown in the top title bar |
| `kind=` | no | `default` | color palette of the title bar |
| `col:` | no | *(none)* | the header row; cells separated by `\|` |
| `row:` | no | *(none)* | a data row; cells separated by `\|` |

A table is a **top-level item**, measured and positioned like a node, so it works
in the stack, `layer` columns, `group` frames and `radial` rings; an `edge` may
target its id (it anchors to the table border).

```fl
table users "users" kind=tablet
col: column | type | key
row: id | uuid | PK
row: email | text | UK
```

- Cells are trimmed; an empty cell renders blank.
- A `col:` after a header already exists warns and is ignored (first wins).
- A row **longer** than the header warns and drops the extra cells; a **shorter**
  row leaves the missing cells blank.
- A `col:`/`row:` with **no** open table warns and is ignored.
- Any other instruction (node, edge, group, layer, radial, …) closes the table.

## `layout` — automatic placement

```fl
layout auto
```

| Parameter | Required | Default | Description |
|---|---|---|---|
| `auto` | yes | — | derive columns from the edges (directed auto-layout) |

`layout auto` places the diagram **left-to-right in edge order**: FlowLite builds
a graph from the edges and derives the columns itself (longest-path layering plus
a crossing-reducing pass), so you write only the edges — no `layer` lines.

```fl
layout auto
edge web -> gw
edge gw -> slip
```

- Only `auto` is valid today; any other value warns and is ignored.
- `layout auto` is **opt-in** — without it the default vertical stack is used.
- An explicit `layer` or `radial` **overrides** auto-layout (a warning notes that
  auto-layout was ignored).

---

> **Planned instructions:** none yet. See the
> roadmap in [`openspec/changes/README.md`](../openspec/changes/README.md).

## CLI

```text
PYTHONPATH=src python3 -m flowlite <input.fl> [-o OUTPUT.svg]
    [--png] [--png-scale N | --png-width W]
```

| Argument | Required | Default | Description |
|---|---|---|---|
| `input` | yes | — | source `.fl` file |
| `-o, --output` | no | `build/<input>.svg` | output SVG path (dirs are created) |
| `--png` | no | off | also export PNG (best-effort via an installed converter) |
| `--png-scale` | no | `2` | PNG scale factor (2× for crisp/HiDPI output) |
| `--png-width` | no | — | PNG pixel width (mutually exclusive with `--png-scale`) |

### PNG export

The compiler is dependency-free; PNG is produced **best effort** by the first
converter found on `PATH`:

`rsvg-convert` · `resvg` · `inkscape` · `chromium`/`google-chrome` · `sips`
(macOS) · `qlmanage` (macOS).

The SVG is always written; if no converter is installed the PNG is skipped, a
hint is printed to stderr (`brew install librsvg`), and the exit code stays `0`.
`--png-scale` and `--png-width` only take effect with `--png` and cannot be
combined.

```bash
# 2x PNG next to the SVG (default)
PYTHONPATH=src python3 -m flowlite examples/hello.fl --png

# a fixed 1600px-wide PNG
PYTHONPATH=src python3 -m flowlite examples/hub.fl --png --png-width 1600
```
