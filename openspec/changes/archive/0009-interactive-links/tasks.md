# Tasks — 0009 Interactive links

## 1. Model + parser

- [x] 1.1 `model.py`: add `link: str = ""` to `Node`.
- [x] 1.2 `parser.py`: parse `link=<url>`; warn on empty value; keep verbatim.
- [x] 1.3 Tests: kept verbatim; empty warns; absent is empty.

## 2. Render

- [x] 2.1 `svg.py`: split `_node` into `_node_body` + wrapper; wrap linked nodes
      in `<a href target rel>`.
- [x] 2.2 Tests: linked node emits `<a>`; plain node does not; href escaped.

## 3. Tests

- [x] 3.1 `tests/test_links.py` (parser, render, determinism).
- [x] 3.2 New golden `tests/golden/index.svg`; existing goldens unchanged.

## 4. Example + docs (required)

- [x] 4.1 `examples/index.fl` — index of the other examples, nodes linking to them.
- [x] 4.2 Commit `docs/img/index.svg` **and** `docs/img/index.png`; embed in gallery.
- [x] 4.3 `reference/language.md` — `link=` row + Interactive subsection; drop it
      from "tolerated but ignored".
- [x] 4.4 `openspec/spec.md` — Interactive links requirement.

## 5. Close out

- [x] 5.1 Archive this change; mark 0009 done in `changes/README.md`.

## Definition of done

- `index.fl` renders nodes wrapped in links to the other examples; no warnings.
- Tests + ruff green; golden + determinism green; sources without `link=`
  unchanged.
- Gallery (svg+png), reference and spec updated; change archived.
