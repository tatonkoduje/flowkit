# Change 0011 — Auto-layout

- **Status:** draft
- **Type:** feature
- **Owner:** maintainers
- **Depends on:** [0001](../archive/0001-walking-skeleton/proposal.md), [0005](../archive/0005-layered-layout/proposal.md)

## Why

Every layout so far is either the naive vertical stack (0001) or an explicit
instruction the author writes by hand (`layer`, `radial`). For a diagram whose
shape is already implied by its **edges** — clients → service → store — asking
the author to name the columns is busywork. A directed (Sugiyama-style)
**auto-layout** derives the columns from the edges: the graph's structure is the
layout.

This is the last roadmap item and closes the loop on
[`docs/RECOMMENDATIONS.md`](../../RECOMMENDATIONS.md) ("pluggable layout:
directed layout first").

## What changes

Add an opt-in directive:

```fl
layout auto
```

When present, FlowLite derives layers from the **edges** and lays the diagram out
left-to-right, instead of the default vertical stack. Nodes are placed so edges
flow left → right.

Algorithm (deterministic, dependency-free):

1. **Layering (longest path).** Build the node graph from the edges
   (groups/tables treated as single items). Assign each node a layer =
   longest directed path from any source, computed on the DAG formed by dropping
   **back edges** (found with a deterministic DFS in declaration order). Roots
   land in layer 0; a node whose predecessors reach depth *k* lands in layer
   *k+1*. Disconnected nodes go to the layer after their last-seen position in
   declaration order (spec: appended to the final layer).
2. **Ordering (barycenter).** Within each layer, order nodes to reduce crossings
   by iterating the barycenter heuristic a fixed number of passes (deterministic:
   ties break by declaration order), then a final stable sort.
3. **Placement.** Reuse the existing `layered` engine: the derived layer per node
   becomes a `Layer`, so columns, gaps, centering and group member grids are all
   shared — no new placement math.
4. **Edges.** Rendered as usual; they now mostly flow left → right.

`layout auto` is **opt-in**: without it, output is exactly as today (stack, or
`layer`/`radial` when declared). With both `layout auto` and an explicit
`layer`/`radial`, the explicit instruction wins (author override) and a warning
notes that auto-layout was ignored.

## Out of scope (later changes)

- True crossing minimization (median/priority methods), node dummy chains
- Horizontal vs vertical direction option (fixed: left → right)
- Auto-layout interacting with `radial`

## Requirements touched

Folds into [`../../spec.md`](../../spec.md):
- Language: `layout auto` directive; derived-layering behavior.

## Example + docs (required)

- New example `examples/auto.fl` — the same pipeline source **without** hand-written
  `layer` lines; auto-layout produces the columns from the edges.
- Committed as `docs/img/auto.svg` **and** `docs/img/auto.png`; embedded in
  `docs/gallery.md`.
- `reference/language.md` — `layout` section.

## Impact

- `src/flowlite/model.py` — add `auto_layout: bool = False` to `Diagram`.
- `src/flowlite/parser.py` — parse `layout auto`; warn on unknown `layout` value.
- `src/flowlite/layout/auto.py` — layering + ordering (new).
- `src/flowlite/compiler.py` — `layout auto` → derive `Layer`s → `layered`.
- Tests: `tests/test_auto.py`; golden `auto.svg`.

## Open questions

- Directive spelling: `layout auto` (chosen) vs `layout=auto` vs bare `auto`?
- Disconnected nodes → trailing layer (chosen) vs layer 0?
