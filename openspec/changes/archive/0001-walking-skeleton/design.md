# Design — 0001 Walking skeleton

## Pipeline

```
.fl text ──parse──▶ Diagram ──measure──▶ sized Diagram ──layout──▶ positioned ──render──▶ SVG
```

Each stage is a **pure function**; data flows through dataclasses. The renderer
never reads source text; layout never emits SVG. This keeps every later feature
(shapes, layouts, icons) a local addition.

## Modules (this change)

| Module | Responsibility |
|---|---|
| `model.py` | frozen dataclasses: `Node`, `Edge`, `Diagram` |
| `parser.py` | text → `Diagram`; warnings, never fatal |
| `themes.py` | load + validate a theme from `themes/<name>.json` |
| `layout/stack.py` | vertical stack in declaration order (placeholder engine) |
| `render/svg.py` | `Diagram` + theme → SVG string |
| `__main__.py` | argparse CLI, paths, exit codes |

Modules not needed yet are **not created** (no empty files).

## Decisions

- **Model = frozen dataclasses.** Immutable, hashable, easy to test.
- **Theme format = JSON.** Zero-dep via `json`; the shape is documented in the
  spec. TOML is deferred.
- **Measurement = char-width token.** `CHAR_W` lives in the theme's tokens; avoids
  font dependencies and keeps output deterministic.
- **Determinism:** iteration is always over explicit lists in declaration order;
  no generated ids, no timestamps.
- **Escaping:** one `esc()` helper applied to every text value.
- **Layout is pluggable.** `stack.py` is intentionally naive; it is the seam that
  `layer`/`radial`/auto-layout will replace or augment later.

## Trade-offs considered

- *Do less vs. do it right.* Chose the smallest slice that still exercises the
  whole spine, so the deterministic + escaping + theming contracts are proven
  from day one.
- *Font metrics vs. char-width.* Char-width can mis-measure, but it is
  deterministic and dependency-free; acceptable for v0 and revisitable.

## Test strategy

- **Unit:** parser per instruction; theme loading incl. unknown-theme error.
- **Golden file:** `examples/hello.fl` → committed `tests/golden/hello.svg`.
- **Determinism:** compile twice, assert byte equality.
- **Escaping:** a label containing `<`, `>`, `&` renders escaped.

## Rollout

Nothing to migrate; the CLI currently returns "not implemented" and will start
producing SVG. Keep the change behind a single merge; update `README.md` status.
