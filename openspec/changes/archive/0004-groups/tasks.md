# Tasks — 0004 Groups

## 1. Model

- [x] 1.1 `model.py`: add `Group`; add `group: str = ""` to `Node`; add `groups` to `Diagram`.

## 2. Parser

- [x] 2.1 Parse `group <id> "Title" [kind=]`.
- [x] 2.2 Parse `in=` on `node`.
- [x] 2.3 Attach members; unknown group id warns and detaches.
- [x] 2.4 Tests: group parsing; membership; unknown `in=`.

## 3. Measurement + layout

- [x] 3.1 `measure.py`: size groups from members (grid math).
- [x] 3.2 `layout/stack.py`: top-level = standalone nodes + groups; members excluded.
- [x] 3.3 Place members in a grid inside the frame.
- [x] 3.4 Tests: frame strictly contains members; member count preserved.

## 4. Rendering

- [x] 4.1 Draw group frames after title, before edges: rounded rect, low-opacity
      kind fill, dashed border, title label.
- [x] 4.2 Edge anchoring to a group id (rect border).
- [x] 4.3 Tests: frame emitted before nodes; group title rendered.

## 5. Tests

- [x] 5.1 `tests/test_groups.py`.
- [x] 5.2 Refresh existing goldens (defs unchanged) + new golden `layers.svg`.

## 6. Example + docs (required)

- [x] 6.1 `examples/layers.fl` — services grouped into frames.
- [x] 6.2 Commit `docs/img/layers.svg` **and** `docs/img/layers.png`; embed in gallery.
- [x] 6.3 `reference/language.md` — `group` section + `in=`.
- [x] 6.4 `openspec/spec.md` — fold in group requirements.

## 7. Close out

- [x] 7.1 Archive this change; mark 0004 done.

## Definition of done

- `layers.fl` renders frames containing their members, with a title and no warnings.
- Tests + ruff green; golden + determinism green.
- Gallery (svg+png), reference and spec updated.
