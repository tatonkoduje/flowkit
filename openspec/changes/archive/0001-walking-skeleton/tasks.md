# Tasks — 0001 Walking skeleton

Checklist is completed top-to-bottom; each item is a small, reviewable step.

## 1. Model

- [ ] 1.1 `model.py`: `Node(id, label, kind)`, `Edge(src, dst)`, `Diagram(title, subtitle, theme, nodes, edges)` as frozen dataclasses.
- [ ] 1.2 Provide `esc()` XML-escaping helper and unit tests.

## 2. Parser

- [ ] 2.1 Regexes for `title`, `theme`, `node`, `edge`.
- [ ] 2.2 `parse(text) -> Diagram`; collect warnings for unknown lines.
- [ ] 2.3 `parse_file(path) -> Diagram`.
- [ ] 2.4 Unknown `kind` falls back to `default` (with a warning).
- [ ] 2.5 Tests: one per instruction; comment/blank lines; unknown line warns.

## 3. Themes

- [ ] 3.1 Define + document the theme JSON shape.
- [ ] 3.2 Author `themes/midnight.json` and `themes/light.json`.
- [ ] 3.3 `load_theme(name) -> Theme`; clear error for unknown name.
- [ ] 3.4 Tests: load both themes; unknown theme raises with the name.

## 4. Measurement + layout

- [ ] 4.1 `measure(node) -> Node` using the theme's `CHAR_W`/`NODE_H`/`PAD_X`.
- [ ] 4.2 `layout/stack.py`: position nodes top-to-bottom, centered; return canvas size.
- [ ] 4.3 Tests: nodes don't overlap; canvas includes margin/title area.

## 5. Renderer

- [ ] 5.1 `render(diagram, theme, w, h) -> str`: `<svg>`, `<defs>` (bg + kind gradients), background.
- [ ] 5.2 Title + subtitle.
- [ ] 5.3 `card` shape: rounded rect, gradient fill, drop shadow, label.
- [ ] 5.4 Edges: bottom-center → top-center, triangle arrow head, no label.
- [ ] 5.5 Golden test: `examples/hello.fl` → `tests/golden/hello.svg`.

## 6. CLI

- [ ] 6.1 Wire `__main__.py` to parse → layout → render → write.
- [ ] 6.2 `-o/--output` (default `build/<input>.svg`, create dirs).
- [ ] 6.3 Exit codes: `0` ok, non-zero on missing input / unknown theme.
- [ ] 6.4 `--help` text.

## 7. Determinism

- [ ] 7.1 Test: compile `examples/hello.fl` twice → byte-identical.

## 8. Example + docs (required)

- [ ] 8.1 Finalize `examples/hello.fl` (the walking-skeleton example).
- [ ] 8.2 Render it to `docs/img/hello.png` and embed it in `docs/gallery.md`.
- [ ] 8.3 Fill `docs/getting-started.md` with the working first-run flow.
- [ ] 8.4 Update `reference/language.md` to match the implemented subset.
- [ ] 8.5 Update `README.md` status (compiler produces SVG for the subset).

## 9. Close out

- [ ] 9.1 Fold requirements into `openspec/spec.md`.
- [ ] 9.2 Archive/remove this change folder.

## Definition of done

- `PYTHONPATH=src python3 -m flowlite examples/hello.fl -o build/hello.svg`
  produces a styled SVG.
- All tests pass; golden + determinism green.
- `examples/hello.fl` is rendered in `docs/gallery.md`; getting-started and the
  language reference match the code.
- No third-party imports in `src/flowlite/`.
