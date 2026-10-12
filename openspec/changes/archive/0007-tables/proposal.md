# Change 0007 — Tables

- **Status:** draft
- **Type:** feature
- **Owner:** maintainers
- **Depends on:** [0001](../archive/0001-walking-skeleton/proposal.md), [0002](../archive/0002-shapes/proposal.md)

## Why

A great many architecture diagrams are really **schemas**: a database table with
its columns, a config object with its fields, a message with its keys. Drawing
those as free-text cards is clumsy — the reader wants aligned columns and a
header. A `table` instruction draws a real table node: a titled header bar and a
grid of rows, with a header row naming the columns.

A table is a first-class top-level item: it is measured, laid out and connected
like any other node, so it composes with the stack, `layer` columns, `group`
frames and `radial` rings, and edges anchor to its border.

## What changes

Add a `table` instruction plus `col:`/`row:` cell lines:

```fl
table <id> "Title" [kind=<kind>]
col: <cell> | <cell> | ...
row: <cell> | <cell> | ...
```

- `table <id> "Title" [kind=]` declares a table and opens it.
- The `col:` line is the **header row**; cells are separated by `|`.
- Each `row:` line is a data row; cells separated by `|`.
- Cells are trimmed; an empty cell renders blank.
- A `col:`/`row:` line with **no** open table warns and is ignored.
- A second `col:` in one table warns and is ignored (header first wins).
- A row may be shorter than the header; missing cells render blank. Extra cells
  beyond the header warn and are dropped.
- A table with no `col:` still renders (headerless) using the widest row.

The table's width fits its widest cell per column; its height is the header plus
one line per row. It participates as a **top-level item** in every layout engine.

## Out of scope (later changes)

- Cell alignment, spanning cells, per-column widths
- Type glyphs / icons inside cells (change 0008)
- Sorting or styling individual cells

## Requirements touched

Folds into [`../../spec.md`](../../spec.md):
- Language: `table <id> "title" [kind=]` with `col:`/`row:` lines.

## Example + docs (required)

- New example `examples/schema.fl` — a small database schema: a `users` table and
  an `orders` table joined by an edge, plus a `group` or column layout to show
  composition.
- Committed as `docs/img/schema.svg` **and** `docs/img/schema.png`; embedded in
  `docs/gallery.md`.
- `reference/language.md` — `table` section.

## Impact

- `src/flowlite/model.py` — add `Table` dataclass (id, title, kind, header, rows);
  add `tables` to `Diagram`.
- `src/flowlite/parser.py` — parse `table`, `col:`, `row:`.
- `src/flowlite/measure.py` — size a table from its cells.
- `src/flowlite/render/svg.py` — draw the table (header bar, rows, grid rules,
  divider lines).
- `src/flowlite/layout/stack.py` (+ `layered`, `radial`) — treat tables as
  top-level items (`_place_members` groups unchanged).
- `src/flowlite/render/svg.py` `_by_id` — tables participate in edge anchoring.
- Tests: `tests/test_tables.py`, golden `schema.svg`.

## Open questions

- Header styling: filled kind-colored bar (chosen) vs uppercase muted label?
- Should a `row:` outside any table warn (chosen) or be a parse error?
