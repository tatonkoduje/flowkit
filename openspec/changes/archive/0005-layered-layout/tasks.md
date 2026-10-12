# Tasks — 0005 Layered layout

## 1. Model

- [x] 1.1 `model.py`: add `Layer`; add `layers` to `Diagram`.

## 2. Parser

- [x] 2.1 Parse `layer <n>: id id id`.
- [x] 2.2 Warn on empty id list; first layer wins for a duplicated id.
- [x] 2.3 Tests: parse ids; empty warns; duplicate membership.

## 3. Layout

- [x] 3.1 `layout/layered.py`: columns from layers; trailing unassigned column.
- [x] 3.2 Center each column vertically; gap between columns.
- [x] 3.3 Reuse member grid placement for groups.
- [x] 3.4 Tests: two columns side-by-side; unassigned trailing; group as member.

## 4. Compiler

- [x] 4.1 Choose layered engine when `diagram.layers`, else stack.

## 5. Tests

- [x] 5.1 `tests/test_layered.py`.
- [x] 5.2 New golden `tests/golden/pipeline.svg`; stack goldens unchanged.

## 6. Example + docs (required)

- [x] 6.1 `examples/pipeline.fl` — client→service→data columns.
- [x] 6.2 Commit `docs/img/pipeline.svg` **and** `docs/img/pipeline.png`; embed in gallery.
- [x] 6.3 `reference/language.md` — `layer` section.
- [x] 6.4 `openspec/spec.md` — fold in layered requirements.

## 7. Close out

- [x] 7.1 Archive this change; mark 0005 done in `changes/README.md`.

## Definition of done

- `pipeline.fl` renders left-to-right columns; unknown ids warn; no warnings on the example.
- Tests + ruff green; golden + determinism green; stack output unchanged.
- Gallery (svg+png), reference and spec updated.
