# Design — 0005 Layered layout

## Model

```python
@dataclass(frozen=True)
class Layer:
    index: int
    ids: tuple[str, ...]
```

`Diagram` gains `layers: tuple[Layer, ...] = field(default_factory=tuple)`,
ordered by declaration. Declaration order of ids within a layer is preserved.

## Parser

Grammar (one per line):

```
layer <n>: id id id
```

Regex: `^layer\s+(\d+)\s*:\s*(.*)$`. Ids are split on whitespace. An empty id
list warns. `<n>` is an int; ordering is by `<n>` at layout time, not by
declaration line.

## Layout

New engine `layout/layered.py`: `layout(diagram, theme) -> (diagram, w, h)` with
the same signature as `stack.layout`.

Two-level, mirroring stack:

1. **Top-level items** = standalone nodes (no group) + groups. A layer id may
   name a node or a group.
2. Assign each top-level item to a column by `<n>`:
   - A node in a layer → that column.
   - A group named in a layer → all items' members stay inside the frame; the
     frame itself goes to that column.
   - Items in no layer → a trailing column, in declaration order (spec).
3. Column widths = max item width in the column; each column is centered
   **vertically** about the canvas center; items stack top-to-bottom within the
   column with `theme.row_gap`.
4. Columns are placed left-to-right in ascending `<n>` order, separated by a
   column gap (theme), then the trailing "unassigned" column.
5. Groups: after the frame is positioned, place members in the same grid as
   stack (`_grid_positions`, shared helper).

Shared helpers (`_grid_positions`, `_place_members`) move to a small private
module or are imported from `stack` to avoid duplication. Keep the seam clean:
`layered.py` may import `stack._grid_positions`.

## Compiler

`compile_diagram` picks the engine:

```python
engine = layered if diagram.layers else stack
positioned, width, height = engine.layout(measured, theme)
```

This keeps 0001–0004 byte-identical (no `layer` → stack).

## Rendering

Unchanged — layers only move boxes; the renderer is engine-agnostic.

## Determinism

Column order = ascending `<n>`; within a column, declaration order; unassigned
run in declaration order. No generated ids, no sorting by hash.

## Test strategy

- Parser: `layer` parsed with ids; empty warns; duplicate-id membership first wins.
- Layout: two columns are side-by-side (non-overlapping x ranges in `<n>` order);
  members of one layer share an x band; unassigned node lands in the trailing
  column; a group can be a layer member.
- Render/golden: `pipeline.fl`.
- Equivalence: a source with no `layer` still equals the stack golden.
