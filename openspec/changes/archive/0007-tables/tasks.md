# Tasks — 0007 Tables

## 1. Model

- [x] 1.1 `model.py`: add `Table` (id, title, kind, header, rows, box); add
      `tables` to `Diagram`; `columns` helper.

## 2. Parser

- [x] 2.1 Parse `table <id> "Title" [kind=]`.
- [x] 2.2 Parse `col:` (header) and `row:` lines; cells split on `|`, trimmed.
- [x] 2.3 Close the open table on any non-cell instruction.
- [x] 2.4 Warn: `col:`/`row:` with no table; duplicate `col:`; over-long row
      (drop extras); duplicate table id.
- [x] 2.5 Tests: parse header+rows; split/trim; each warning; short row allowed.

## 3. Measure

- [x] 3.1 `measure.py`: size a table (column widths from widest cell, min width;
      height = header + rows).
- [x] 3.2 Tests: width grows with cells; height formula; headerless column count.

## 4. Layout

- [x] 4.1 Add tables to the top-level item list in `stack`, `layered`, `radial`.
- [x] 4.2 Tests: table placed in stack/layered/radial with non-zero size.

## 5. Render

- [x] 5.1 `svg.py`: draw body, header bar (title), row/header rules, column
      dividers and cell text.
- [x] 5.2 `_by_id`/`_as_rect`: tables anchor edges to their border.
- [x] 5.3 Tests: header + cells rendered (escaped); edge to a table id.

## 6. Tests

- [x] 6.1 `tests/test_tables.py`.
- [x] 6.2 New golden `tests/golden/schema.svg`; existing goldens unchanged.

## 7. Example + docs (required)

- [x] 7.1 `examples/schema.fl` — two related tables with an edge.
- [x] 7.2 Commit `docs/img/schema.svg` **and** `docs/img/schema.png`; embed in gallery.
- [x] 7.3 `reference/language.md` — `table`/`col:`/`row:` section; drop from planned.
- [x] 7.4 `openspec/spec.md` — flesh out the Tables requirement.

## 8. Close out

- [x] 8.1 Archive this change; mark 0007 done in `changes/README.md`.

## Definition of done

- `schema.fl` renders tables with headers and rows; edges reach table borders;
  no warnings on the example.
- Tests + ruff green; golden + determinism green; existing goldens unchanged.
- Gallery (svg+png), reference and spec updated; change archived.
