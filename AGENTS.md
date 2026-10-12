# AGENTS.md — guidance for AI coding assistants

This file tells AI coding assistants how to work in the **FlowLite** repository.

## What this project is

FlowLite is a **minimal, deterministic, dependency-free** compiler that turns a
tiny text DSL (`.fl`) into **beautiful, presentation-ready SVG/PNG diagrams**. It
is the successor design to the internal `flowkit` tool — read
[`docs/RECOMMENDATIONS.md`](docs/RECOMMENDATIONS.md) for context and direction.

Read first: [`README.md`](README.md) → [`docs/RECOMMENDATIONS.md`](docs/RECOMMENDATIONS.md)
→ [`openspec/spec.md`](openspec/spec.md).

## Non-negotiable principles

1. **Minimal surface area.** Fewer keywords, fewer options, sane defaults.
2. **Deterministic output.** Same input → byte-identical SVG. No timestamps, no
   randomness, stable ordering.
3. **Standard library only** in `src/flowlite/`. Optional PNG export may shell
   out to external tools, never import third-party packages.
4. **Beauty is a contract.** Default colors, spacing and typography are public
   behavior; changing them is breaking.
5. **Always XML-escape** user text before writing SVG.

## Layout

| Path | Purpose |
|---|---|
| `src/flowlite/` | the compiler package (stdlib only) |
| `src/flowlite/model.py` | dataclasses + XML escaping |
| `src/flowlite/parser.py` | `.fl` text → model |
| `src/flowlite/measure.py` | per-shape node sizing |
| `src/flowlite/shapes/` | vertices and border anchors |
| `src/flowlite/layout/` | layout engines (currently `stack.py`) |
| `src/flowlite/render/` | SVG rendering |
| `src/flowlite/compiler.py` | the pipeline |
| `themes/` | theme definitions (data) |
| `tests/` | test suite (+ golden SVGs) |
| `openspec/` | specification + change proposals |
| `docs/` | getting-started, gallery, recommendations |
| `reference/` | the language reference |

The pipeline is implemented (change `0001-walking-skeleton`): `model.py`,
`parser.py`, `measure.py`, `layout/stack.py`, `render/svg.py`, `themes.py`,
`compiler.py`. New modules are added only when a change needs them — do not
create empty files ahead of need. See [`openspec/changes/README.md`](openspec/changes/README.md)
for the roadmap.

## Commands

```bash
# run the CLI (package lives in src/)
PYTHONPATH=src python3 -m flowlite examples/hello.fl -o build/hello.svg --png

# tests
PYTHONPATH=src python3 -m pytest
```

If you add a lint/typecheck command, add it to `CONTRIBUTING.md` **and** here.

## Working process

- **Spec-first.** For significant changes, create an OpenSpec proposal in
  `openspec/changes/<change-id>/` before writing code. Trivial fixes don't need one.
- **Every change ships an example and docs.** A change is not done until it adds
  or extends an example in `examples/`, commits **both** `docs/img/<name>.svg`
  and `docs/img/<name>.png`, and updates `reference/language.md` (and
  `docs/getting-started.md` when the first-run flow changes). Docs are a
  deliverable, not an afterthought.
- **One logical change per PR.** Keep diffs tight.
- **Tests required** for parser, layout and rendering behavior. Golden-file SVG
  tests are encouraged.
- Do not commit secrets or generated artifacts.

## Conventions

- Python 3.10+; 4-space indent; type hints on public functions.
- Prefer pure functions for parse/measure/layout/render.
- Comments only where the code isn't self-evident.
