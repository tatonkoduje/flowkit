# Tasks — 0008 Icons

## 1. Icon data + loader

- [x] 1.1 `icons/lucide.json` — vendored curated lucide subset (name → path d,
      with meta/license).
- [x] 1.2 `src/flowlite/icons.py` — `all_icons()` + `icon_path(name)`.

## 2. Model + parser

- [x] 2.1 `model.py`: add `icon: str = ""` to `Node`.
- [x] 2.2 `parser.py`: parse `icon=<name>`; warn and clear on unknown name.
- [x] 2.3 Tests: known kept; unknown warns; absent is empty.

## 3. Render

- [x] 3.1 `svg.py`: draw the icon tinted white; place it per shape (left of label
       for wide shapes, above the label for hub/polyN).
- [x] 3.2 Tests: icon path emitted; no icon → none; tinted stroke.

## 4. Tests

- [x] 4.1 `tests/test_icons.py` (loader, parser, render, determinism).
- [x] 4.2 Regenerate goldens for the extended examples; verify no-icon sources
       unchanged.

## 5. Example + docs (required)

- [x] 5.1 Extend `examples/hello.fl`, `shapes.fl`, `hub.fl`, `schema.fl` with icons.
- [x] 5.2 Re-commit affected `docs/img/*.svg` **and** `.png`; gallery captions.
- [x] 5.3 `reference/language.md` — `icon=` row + Icons subsection (name list).
- [x] 5.4 `openspec/spec.md` — Icons requirement.

## 6. Close out

- [x] 6.1 Archive this change; mark 0008 done in `changes/README.md`.

## Definition of done

- Examples render with kind-tinted icons; unknown icon names warn; no warnings on
  the examples.
- Tests + ruff green; goldens + determinism green; no-icon sources unchanged.
- Gallery (svg+png), reference and spec updated; change archived.
