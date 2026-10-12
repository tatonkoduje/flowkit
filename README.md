# FlowLite

**Beautiful diagrams from plain text — minimal, deterministic, dependency-free.**

FlowLite turns simple `.fl` text into **presentation-ready SVG/PNG diagrams** with
gradient cards, soft shadows, real icons and clean connectors — the kind of
graphics architects and developers want in a design review.

Think of it as *"Mermaid, but dressed for a design review"* — and small enough to
read in an afternoon.

> **Status: early.** Changes 0001-0003 are implemented: `title`, `theme`, `node`
> (with `kind=` and `shape=`), `edge` (labels, `style=`, `arrow=`, `curve=`), the
> shapes `card`/`db`/`hub`/`hex`/`pill`/`diamond`/`polyN` with per-shape edge
> anchoring, a vertical stack layout, the `midnight`/`light` themes and the CLI.
> More layouts and features follow as small changes; see
> [`openspec/changes/`](openspec/changes/).

## Why FlowLite

- **Minimal** — a tiny DSL, a tiny compiler, no build step.
- **Beautiful by default** — gradients, shadows, icons and curated themes out of the box.
- **Deterministic** — text in, byte-stable SVG out; diffable and reviewable.
- **Dependency-free** — pure Python 3 standard library.

## Quick start

```bash
# package lives in src/
PYTHONPATH=src python3 -m flowlite examples/hello.fl -o build/hello.svg --png
```

```fl
title "My service" "a first FlowLite diagram"
theme midnight

node api "API Gateway" kind=gateway
node db  "PostgreSQL"  kind=store shape=db

edge api -> db
```

### Output formats

**SVG is always written** — it is the primary, vector output and opens in any
IDE or browser. PNG is optional and best-effort:

```bash
PYTHONPATH=src python3 -m flowlite diagram.fl            # -> build/diagram.svg
PYTHONPATH=src python3 -m flowlite diagram.fl --png      # -> build/diagram.svg + .png
```

## Repository layout

```text
flowlite/
├── src/flowlite/        # the compiler package (stdlib only)
│   ├── model.py         # dataclasses + XML escaping
│   ├── parser.py        # .fl text -> model
│   ├── themes.py        # theme loading
│   ├── measure.py       # node sizing
│   ├── layout/stack.py  # vertical stack layout
│   ├── render/svg.py    # model -> SVG
│   ├── compiler.py      # the pipeline
│   └── __main__.py      # CLI entry point
├── themes/              # theme definitions (data)
├── examples/            # example sources (*.fl)
├── tests/               # test suite (+ golden SVGs)
├── openspec/            # the specification + change proposals
├── docs/                # getting-started, gallery, recommendations
├── reference/           # the language reference
└── AGENTS.md            # guidance for AI coding assistants
```

## Documentation

| Document | Content |
|---|---|
| [Getting started](docs/getting-started.md) | install, first diagram, compiling |
| [Language reference](reference/language.md) | every instruction and attribute |
| [Gallery](docs/gallery.md) | rendered examples |
| [Specification](openspec/spec.md) | requirements and scenarios |
| [Recommendations](docs/RECOMMENDATIONS.md) | Mermaid + FlowKit analysis and the FlowLite direction |
| [Change proposals](openspec/changes/) | planned work, one small change at a time |

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). FlowLite is built spec-first: significant
changes start as a proposal in [`openspec/changes/`](openspec/changes/) before any
code is written.

## License

MIT — see [LICENSE](LICENSE). Bundled icons are from [lucide](https://lucide.dev)
(ISC license).
