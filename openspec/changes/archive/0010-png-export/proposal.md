# Change 0010 — PNG export

- **Status:** draft
- **Type:** feature
- **Owner:** maintainers
- **Depends on:** [0001](../archive/0001-walking-skeleton/proposal.md)

## Why

The SVG is the readable, vector-first artifact, but a **PNG** is what people
paste into slides, issues and chat. The gallery rule (see
[`../README.md`](../README.md)) already requires **both** `.svg` and `.png` for
every example. Today `--png` exists but is thin: it tries three converters with
one fixed scale and a hand-rolled `qlmanage` path, and there are no tests.

This change hardens PNG export so `--png` produces **crisp, predictable** images
in more environments — while keeping the project's promise: **no third-party
imports**, the compiler stays pure, and PNG is *best effort* via whatever
external converter the machine has.

## What changes

Strengthen the CLI's PNG path:

- **More converters**, tried in a deterministic order:
  `rsvg-convert` → `resvg` → `inkscape` → `chromium`/`google-chrome` (headless) →
  `sips` (macOS) → `qlmanage` (macOS fallback).
- **Correct, per-tool argument forms** (each converter has its own flags; the
  current `inkscape` call is malformed).
- **Scale control**: `--png-scale N` (default `2`, for crisp output on HiDPI) and
  `--png-width W` (explicit pixel width) — at most one may be given; both are
  passed to converters that support sizing, and the others fall back to their
  default.
- **Clear, actionable messages**: on success the PNG path is printed; when no
  converter is found the message names one concrete install
  (`brew install librsvg`) and the exit code stays `0` (the SVG *was* written —
  PNG is best effort, matching the existing spec scenario).
- The whole switch lives behind **one function** `svg_to_png(svg_path, png_path,
  scale, width) -> str | None` returning the converter name used (or `None`), so
  it is unit-testable without any real converter.

## Out of scope (later changes)

- Bundling/pure-Python rasterization (violates the no-dependency rule)
- `--png` for a directory of sources (batch/gallery mode)
- Transparent background / custom DPI metadata

## Requirements touched

Folds into [`../../spec.md`](../../spec.md):
- Rendering: PNG export converters, sizing options, best-effort messaging.

## Example + docs (required)

- No new diagram (this is a toolchain change). Instead: **regenerate every
  gallery `.png`** through the hardened path so the documented images match what
  the tool now produces, and note the export options in the reference.
- `reference/language.md` — update the CLI table: `--png`, `--png-scale`,
  `--png-width`; list supported converters.

## Impact

- `src/flowlite/__main__.py` — rewrite `to_png` into `svg_to_png`; add
  `--png-scale`/`--png-width`; wire messages.
- `tests/test_cli.py` — add tests with a fake converter on `PATH` (a tiny shell
  script in `tmp_path`), covering: converter found and used; scale/width flags
  forwarded; no converter → SVG still written, name in stderr, exit `0`; both
  sizing flags together is an error.

## Open questions

- Default scale `2` (chosen) vs `1`?
- `--png-width` and `--png-scale` are mutually exclusive (chosen) vs width wins?
