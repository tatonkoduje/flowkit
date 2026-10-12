# Tasks — 0010 PNG export

## 1. Exporter

- [x] 1.1 `__main__.py`: replace `to_png` with `svg_to_png(svg, png, scale, width)`
      returning the converter name or `None`.
- [x] 1.2 Add converters in fixed order: rsvg-convert, resvg, inkscape, chromium,
      sips, qlmanage — with correct per-tool arguments.
- [x] 1.3 Read the SVG's intrinsic width/height to compute scale/width sizes.

## 2. CLI

- [x] 2.1 Add `--png-scale` (default 2) and `--png-width` (mutually exclusive with
      scale); warn when given without `--png`.
- [x] 2.2 Print `wrote <png> (via <name>)`; on no converter print an install hint
      to stderr and keep exit `0`.

## 3. Tests

- [x] 3.1 `tests/test_cli.py`: fake converter on PATH — used, flags forwarded.
- [x] 3.2 No converter (empty PATH): SVG written, exit 0, stderr hint.
- [x] 3.3 `--png-scale` + `--png-width` together → exit 2, no SVG.

## 4. Docs

- [x] 4.1 `reference/language.md` — CLI table: `--png`, `--png-scale`,
      `--png-width` + supported converters list.
- [x] 4.2 `openspec/spec.md` — PNG export converters/sizing/messaging requirement.
- [x] 4.3 Regenerate all gallery `.png` via the hardened path.

## 5. Close out

- [x] 5.1 Archive this change; mark 0010 done in `changes/README.md`; CHANGELOG.

## Definition of done

- `--png` writes a PNG via the first available converter (rsvg-convert here) and
  reports which; sizing flags work; no-converter stays best-effort (exit 0).
- Tests + ruff green; SVGs unchanged (goldens intact).
- Reference/spec updated; gallery PNGs regenerated; change archived.
