# Design — 0011 Auto-layout

## Model

`Diagram` gains `auto_layout: bool = False`. `False` (default) → the compiler
behaves exactly as today, so every existing golden is byte-identical.

## Parser

Grammar (one instruction per line):

```
layout auto
```

`LAYOUT_RE = re.compile(r"^layout\s+(\w+)\s*$")`. `auto` sets `auto_layout=True`.
Any other value warns (`unknown layout '<v>', expected 'auto'`) and is ignored.
`layout auto` may appear anywhere; it is a diagram-level flag, not positional.

## Layering

New module `layout/auto.py`:

```python
def derive_layers(diagram: Diagram) -> tuple[Layer, ...]: ...
```

1. **Items.** Top-level items = standalone nodes + groups + tables, in
   declaration order (same convention as the other engines). An edge between two
   members of the same group is internal; edges between items use the item id
   (a node id, or a group/table id via the node's `group`).
2. **Item graph.** For each edge `a -> b`, map `a`/`b` to their top-level item id
   (a grouped node maps to its group; an edge may name a group/table directly).
   Drop self-loops; keep the first occurrence of a duplicate pair.
3. **Back edges.** DFS from each item in declaration order, visiting out-edges in
   edge-declaration order; an edge to a node currently on the DFS stack is a
   **back edge** and is dropped. This makes the graph a DAG deterministically.
4. **Longest-path layering.** On the DAG, `layer(v) = max(layer(u)+1)` over
   predecessors `u`; sources (no predecessors) are layer 0. Compute with a
   topological order (Kahn) so it is a single pass.
5. **Isolated/disconnected items** (no edges): assigned to a trailing layer
   (max layer + 1) in declaration order — matching the layered engine's
   "unassigned trail" spirit.
6. Return `Layer(index=k, ids=(...))` for each non-empty layer, ids in
   declaration order.

## Ordering (barycenter)

`order_layers(layers, edges, passes=4) -> layers`:

- Initial order = declaration order.
- For `passes` sweeps (down then up), set each node's key to the average index of
  its neighbours in the adjacent already-ordered layer; sort each layer by that
  key with a **stable** sort (ties keep the previous order → deterministic).
- Nodes with no neighbours keep their position.

Fixed `passes` and stable sorts make the result a pure function of the input.

## Compiler

```python
if diagram.radial:
    engine = radial
elif diagram.layers:
    engine = layered
elif diagram.auto_layout:
    derived = auto.derive_layers(measured)
    positioned, w, h = layered.layout(
        replace(measured, layers=derived), theme
    )
    return svg.render(positioned, theme, w, h)
else:
    engine = stack
```

If `auto_layout` and `layers` are both present, the explicit `layers` branch wins
(author override); the parser does not warn (both are legal), but the reference
documents the precedence. (Alternatively the parser could warn — chosen: **warn**
in the parser when `layout auto` coexists with a `layer` line, to be helpful.)

Wait — the parser sees `layer`/`layout` in any order; simplest is to warn at the
end of parsing if `auto_layout and layers`. Decision: **warn** and keep the
explicit layers.

## Rendering

Unchanged — auto-layout only produces positions.

## Determinism

Declaration-order iteration, DFS edge order, Kahn topological order (queue seeded
in declaration order), stable sorts, fixed pass count. No randomness, no hashing.

## Test strategy

- Parser: `layout auto` sets the flag; unknown value warns; coexists-with-layer
  warns.
- Layering: a simple `a->b->c` chain → three layers; a diamond `a->b, a->c, b->d,
  c->d` → a and d at the ends; a cycle (`a->b->a`) does not hang and drops the
  back edge; a disconnected node trails.
- Layout: derived columns are left-to-right in edge-flow order; a chain renders
  in order.
- Equivalence: without `layout auto`, goldens unchanged.
- Golden: `auto.fl`.
