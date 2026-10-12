# Design — 0007 Tables

## Model

```python
@dataclass(frozen=True)
class Table:
    id: str
    title: str
    kind: str = "default"
    header: tuple[str, ...] = ()
    rows: tuple[tuple[str, ...], ...] = ()
    # Assigned by measurement.
    width: float = 0.0
    height: float = 0.0
    # Assigned by layout.
    x: float = 0.0
    y: float = 0.0

    @property
    def columns(self) -> int:
        return len(self.header) or max((len(r) for r in self.rows), default=0)
```

`Diagram` gains `tables: tuple[Table, ...] = field(default_factory=tuple)`.

## Parser

Grammar (one instruction per line):

```
table <id> "Title" [kind=<kind>]
col: <cell> | <cell> | ...
row: <cell> | <cell> | ...
```

Regexes:

```python
TABLE_RE = re.compile(r'^table\s+(\w+)\s+"([^"]*)"(.*)$')
COL_RE   = re.compile(r"^col\s*:\s*(.*)$")
ROW_RE   = re.compile(r"^row\s*:\s*(.*)$")
```

State: `current_table: int | None` — index of the table being filled while
`col:`/`row:` lines arrive. `table` sets it; any other instruction (node/edge/
group/layer/radial/title/theme) **closes** it. `col:`/`row:` without an open
table warn and are ignored.

Cell split: `[c.strip() for c in line.split("|")]`. A trailing/leading `|` makes
an empty cell, matching spreadsheet intuition.

Validation (warnings, never fatal):
- `col:` when a header already exists → warn, ignore.
- `row:` longer than the header (or `col:`) → extra cells dropped, warn.
- `row:` shorter → allowed; missing cells blank at render.

Duplicate table ids: the later one warns and is ignored (first wins) — consistent
with layers/groups.

## Measurement

Constants (module-level, deterministic):

```python
TABLE_CELL_PAD_X = 14.0
TABLE_CELL_PAD_Y = 9.0
TABLE_HEADER_H = 34.0
TABLE_ROW_H = 28.0
TABLE_MIN_COL_W = 64.0
TABLE_MIN_WIDTH = 180.0
```

- Column widths: `max(len(cell) * char_width for cell in column) + 2*pad_x`,
  floored at `TABLE_MIN_COL_W`. Width per column is the max over the header cell
  and every row cell in that column.
- `width = max(TABLE_MIN_WIDTH, sum(col_widths))`.
- `height = TABLE_HEADER_H + len(rows) * TABLE_ROW_H` (header always present;
  a table with no rows is just the header bar).

The table is a **top-level item** with `.width`/`.height` and `.x`/`.y`, so it
drops into `stack`, `layered`, `radial` with no engine changes beyond including
it in the item list.

## Layout

Top-level item lists in `stack.py`, `layered.py`, `radial.py` currently build
`items = [*standalone_nodes, *groups]`. Add tables:

```python
items = [*standalone_nodes, *groups, *diagram.tables]
```

Tables are never group members (a table is standalone). Ordering: tables are
appended after groups in declaration order; this is deterministic. (Declaration
order across kinds is not preserved — nodes, then groups, then tables — which
matches the existing nodes-then-groups convention.)

## Rendering

`svg._table(table, theme)` draws, back to front:

1. A rounded body rect filled with the kind gradient (low opacity) and a border,
   under the existing shadow filter.
2. A **header bar**: a kind-colored filled rounded-top rect with the table title
   (left, bold, small caps like group titles) — optionally the `col:` cells as a
   second header line.
3. Column **divider rules** (thin, low-opacity) between columns.
4. A **rule** under the header and under each row.
5. Cell text, left-aligned within each column, vertically centered in its row.

Because cell text can be long, each cell is drawn with `esc()`.

`_by_id` gains tables so `edge a -> users` anchors to the table border:

```python
def _as_rect(item):
    if isinstance(item, (Group, Table)):
        return Node(id=item.id, label=..., shape="card",
                    width=item.width, height=item.height, x=item.x, y=item.y)
```

## Determinism

Column widths and row order come straight from declaration; no sorting. Text is
drawn in a fixed order (header, rules, then cells row-major). Same input →
byte-identical SVG.

## Test strategy

- Parser: `table` + `col:` + `row:` parsed; cells split/trimmed; `col:` without a
  table warns; duplicate `col:` warns; over-long row warns and drops extras;
  short row allowed; table closes on the next non-cell instruction.
- Measure: width grows with longer cells; height = header + rows*row_h; column
  count from header, from widest row when headerless.
- Layout: a table is a top-level item in stack/layered/radial (placed, non-zero
  size); an edge targets a table id.
- Render: header title present; each cell text present (escaped); dividers count.
- Golden: `schema.fl`.
- Equivalence: existing goldens unchanged (no tables → identical output).
