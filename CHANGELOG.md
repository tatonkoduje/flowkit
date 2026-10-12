# Changelog

All notable changes to FlowLite are documented here.
The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Initial repository scaffolding: package layout, docs, OpenSpec, CI.
- Specification in [`openspec/spec.md`](openspec/spec.md).
- Design recommendations in [`docs/RECOMMENDATIONS.md`](docs/RECOMMENDATIONS.md).
- `radial` layout (`radial hub=<id> [radius=] [start=] [dock] [gap=]`) with
  polygon-face docking (change 0006).
- `table` nodes (`table <id> "title" [kind=]` with `col:`/`row:` cell lines),
  measured, laid out and edge-connectable as top-level items (change 0007).
- Node icons (`icon=<name>`) drawn tinted by `kind`, from a vendored lucide
  subset (`icons/lucide.json`, ISC) — no runtime dependency (change 0008).
- Interactive nodes (`link=<url>`) rendered as SVG hyperlinks opening in a new
  tab (change 0009).
- `layout auto` — directed (Sugiyama-style) auto-layout deriving columns from
  the edges (change 0011).

### Changed

- Hardened best-effort PNG export: more converters (rsvg-convert, resvg,
  inkscape, chromium, sips, qlmanage), correct per-tool arguments, and
  `--png-scale` (default 2×) / `--png-width` sizing (change 0010).

### Fixed

- `hex` shapes now anchor edges to the hexagon actually drawn (full-width
  flat-topped hexagon) instead of an inscribed regular polygon, so connectors
  meet the border instead of stopping inside the shape.

[Unreleased]: https://github.com/OWNER/flowlite/commits/main
