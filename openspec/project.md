# Project: FlowLite

## Purpose

FlowLite compiles a minimal text DSL into **beautiful, deterministic, dependency-free**
SVG/PNG diagrams, aimed at architects and developers who value presentation-quality
graphics.

## Principles

1. **Minimal surface area** — few keywords, great defaults.
2. **Deterministic output** — same input, byte-identical SVG.
3. **Standard library only** in the core.
4. **Beauty is a contract** — default looks are versioned behavior.
5. **Aesthetics are data** — themes and icons live in files, not code.

## Stack

- Python 3.10+, standard library only.
- pytest for tests.
- Optional external converters for PNG (`rsvg-convert`, `inkscape`, `qlmanage`).

## Conventions

- One DSL: `.fl`.
- Spec-first: significant changes go through `openspec/changes/`.
- **Every change ships an example + docs** (getting-started / language reference /
  gallery). Gallery examples are committed as **both `.svg` and `.png`**. See the
  golden rule in [`changes/README.md`](changes/README.md).
- See [`../AGENTS.md`](../AGENTS.md) for the full working agreement.
