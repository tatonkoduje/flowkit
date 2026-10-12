# Tasks — 0011 Auto-layout

## 1. Model + parser

- [x] 1.1 `model.py`: add `auto_layout: bool = False` to `Diagram`.
- [x] 1.2 `parser.py`: parse `layout auto`; warn on unknown value; warn when it
      coexists with an explicit `layer`.
- [x] 1.3 Tests: flag set; unknown value warns; layer coexistence warns.

## 2. Auto layout

- [x] 2.1 `layout/auto.py`: build the top-level item graph from edges.
- [x] 2.2 Longest-path layering on the DAG (drop back edges via deterministic DFS).
- [x] 2.3 Barycenter ordering (fixed passes, stable) to reduce crossings.
- [x] 2.4 Disconnected items trail; return `Layer`s.
- [x] 2.5 Tests: chain; diamond; cycle is safe; disconnected trails.

## 3. Compiler

- [x] 3.1 `layout auto` derives layers and runs the `layered` engine; explicit
      `layer`/`radial` still win.

## 4. Tests

- [x] 4.1 `tests/test_auto.py`.
- [x] 4.2 New golden `tests/golden/auto.svg`; existing goldens unchanged.

## 5. Example + docs (required)

- [x] 5.1 `examples/auto.fl` — a pipeline with no explicit `layer`.
- [x] 5.2 Commit `docs/img/auto.svg` **and** `docs/img/auto.png`; embed in gallery.
- [x] 5.3 `reference/language.md` — `layout` section.
- [x] 5.4 `openspec/spec.md` — Auto-layout requirement.

## 6. Close out

- [x] 6.1 Archive this change; mark 0011 done in `changes/README.md`; CHANGELOG.

## Definition of done

- `auto.fl` renders edge-derived left→right columns; no warnings on the example.
- Tests + ruff green; golden + determinism green; sources without `layout auto`
  unchanged.
- Gallery (svg+png), reference and spec updated; change archived.
