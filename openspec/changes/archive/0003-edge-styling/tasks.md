# Tasks — 0003 Edge styling

## 1. Model

- [ ] 1.1 `model.py`: add `label`, `style`, `arrow`, `curve` to `Edge` (with defaults).

## 2. Parser

- [ ] 2.1 Parse an optional quoted label after `-> <to>`.
- [ ] 2.2 Parse `style=`/`arrow=`/`curve=` in any order.
- [ ] 2.3 Unknown values warn and fall back to defaults.
- [ ] 2.4 Tests: label; each attribute; order-independence; unknown values.

## 3. Theme

- [ ] 3.1 Expose `label_background`/`label_text` on `Theme`.

## 4. Renderer

- [ ] 4.1 Add `#arrow-dot` marker; keep `#arrow`.
- [ ] 4.2 `style=dashed` → dash array; `style=bold` → thicker stroke.
- [ ] 4.3 `arrow=dot`/`none` → dot marker / no marker.
- [ ] 4.4 `curve=straight` → line; `curve=bezier` → curve.
- [ ] 4.5 Label pill + text at the midpoint (escaped).

## 5. Tests

- [ ] 5.1 `test_render.py`: one test per attribute behavior.
- [ ] 5.2 New golden `tests/golden/flow.svg`.

## 6. Example + docs (required)

- [ ] 6.1 `examples/flow.fl` — labelled, typed edges.
- [ ] 6.2 Commit `docs/img/flow.svg` **and** `docs/img/flow.png`; embed in gallery.
- [ ] 6.3 `reference/language.md` — `edge` table.
- [ ] 6.4 `openspec/spec.md` — fold in edge requirements.

## 7. Close out

- [ ] 7.1 Archive this change; mark 0003 done in `changes/README.md`.

## Definition of done

- `flow.fl` renders labelled edges with correct styles/markers/curves, no warnings.
- Tests + ruff green; golden + determinism green.
- Gallery (svg+png), reference and spec updated.
