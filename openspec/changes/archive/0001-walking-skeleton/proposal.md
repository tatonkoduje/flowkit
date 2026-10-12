# Change 0001 — Walking skeleton

- **Status:** draft
- **Type:** feature (foundation)
- **Owner:** maintainers
- **Depends on:** —

## Why

FlowLite has a spec and a repo, but nothing runs end to end. Before adding
breadth we prove the **pipeline and the deterministic contract** on the smallest
possible slice, so every later feature lands on a spine that already works.

This is the first of a **sequence of small changes** (see [`README.md`](README.md)).
It deliberately does *not* implement the whole FlowKit feature set.

## What changes

A working vertical slice:

1. **Model + parser** for a minimal subset:
   `title`, `theme`, `node` (label + `kind=`), and `edge`.
2. **Measure + a single layout**: a trivial left-to-right/vertical stack in
   declaration order (no `layer`, no `radial` yet).
3. **SVG renderer** for one shape (`card`) with a gradient fill and the theme
   background — the aesthetic baseline.
4. **Theme loading** from `themes/*.json` for `midnight` and `light`.
5. **CLI** wired to the pipeline: `python3 -m flowlite in.fl -o out.svg`.
6. **Tests**: parser unit tests + a golden-file SVG test + a determinism test.
7. **Example + docs** (required — see the golden rule in
   [`../README.md`](../README.md)): `examples/hello.fl`, rendered and referenced
   in [`../../docs/gallery.md`](../../docs/gallery.md), plus
   [`../../docs/getting-started.md`](../../docs/getting-started.md) and
   [`../../reference/language.md`](../../reference/language.md) reflecting the
   subset.

## Explicitly out of scope (later changes)

- Shapes beyond `card` (`db`, `hub`, `hex`, `pill`, `diamond`, `polyN`, `table`)
- Groups, `layer` columns, `radial`/dock layout
- Edge labels, styles, curves, arrow variants
- Icons, clickable `link=` nodes
- PNG export

Each of the above gets its own change request so it can be reviewed and tested
in isolation.

## Requirements touched

Folds into [`../../spec.md`](../../spec.md):
- Language: header, nodes, edges (subset).
- Rendering: vector-first output, presentation defaults, deterministic, safe text.
- Theming: themes as data, unknown theme fails clearly.
- CLI: entry point, `-o/--output`, exit codes, `--help`.

## Impact

- New code: `src/flowlite/{model,parser,themes,__main__}.py`,
  `src/flowlite/render/svg.py`, `src/flowlite/layout/stack.py`.
- Themes: `themes/midnight.json`, `themes/light.json`.
- Tests: `tests/test_parser.py`, `tests/test_render.py`, `tests/test_determinism.py`.
- Examples: `examples/hello.fl`.
- Docs: `docs/getting-started.md`, `reference/language.md`, `docs/gallery.md`.

## Open questions

- Theme file format: JSON vs TOML. Leaning **JSON** (zero-dep `json`; TOML via
  `tomllib` is read-only and 3.11+). See [`design.md`](design.md).
- Label measurement: keep a `CHAR_W` token (FlowKit approach) vs. real font
  metrics. Leaning **token** for determinism and zero deps.
