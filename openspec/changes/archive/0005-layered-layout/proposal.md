# Change 0005 — Layered layout

- **Status:** draft
- **Type:** feature
- **Owner:** maintainers
- **Depends on:** [0001](../archive/0001-walking-skeleton/proposal.md), [0002](../archive/0002-shapes/proposal.md), [0004](../archive/0004-groups/proposal.md)

## Why

A vertical stack reads top-to-bottom, but architectures usually flow
**left-to-right**: clients, then services, then data. A `layer` instruction lets
the author assign nodes to named columns so the picture reads as a pipeline,
while everything else keeps the default stack behavior.

## What changes

Add a `layer` instruction that groups nodes into ordered columns:

```fl
layer <n>: <id> [<id> ...]
```

- `<n>` is a positive integer ordering the columns left-to-right.
- Members are listed as space-separated node ids.
- Each column is centered vertically; columns are laid out left-to-right in
  ascending `<n>` order, separated by the theme gap.
- Edges attach to real shape borders, so a left→right pipeline reads cleanly.
- A node id that matches no node warns and is ignored.
- A node may appear in at most one layer; a later assignment warns and is ignored
  (first wins).
- Interactive with groups: a grouped node's members live inside their frame;
  layers apply to **top-level items** (standalone nodes and groups). A layer id
  may name a **group id** to place the whole frame in that column.

When **no** `layer` instruction is present, the existing vertical stack is used
unchanged.

## Out of scope (later changes)

- Auto-deriving layers from edges (the directed layout in change 0011)
- Per-layer alignment, spacing or wrapping
- Mixing layers and radial in one diagram

## Requirements touched

Folds into [`../../spec.md`](../../spec.md):
- Language: `layer <n>: ids` instruction.

## Example + docs (required)

- New example `examples/pipeline.fl` — a client→service→data pipeline.
- Committed as `docs/img/pipeline.svg` **and** `docs/img/pipeline.png`; embedded
  in `docs/gallery.md`.
- `reference/language.md` — `layer` section.

## Impact

- `src/flowlite/model.py` — add `layers: tuple[Layer, ...]` to `Diagram`;
  `Layer` dataclass.
- `src/flowlite/parser.py` — parse `layer <n>: ids`.
- `src/flowlite/layout/layered.py` — new engine (columns, centered).
- `src/flowlite/compiler.py` — choose engine: layered when layers exist, else stack.
- Tests: `tests/test_layered.py`, render/golden.

## Open questions

- Column vertical alignment: center each column (chosen) vs top-align?
- Should a `layer` with no members be an error or an empty column?
