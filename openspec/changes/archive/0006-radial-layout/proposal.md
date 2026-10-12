# Change 0006 — Radial layout

- **Status:** draft
- **Type:** feature
- **Owner:** maintainers
- **Depends on:** [0001](../archive/0001-walking-skeleton/proposal.md), [0002](../archive/0002-shapes/proposal.md)

## Why

Some diagrams are not a pipeline and not a stack: they are a **hub and its
spokes**. An event bus with producers and consumers, a gateway with clients, a
core with satellites — these read best as a central node with members arranged
around it. A `radial` instruction places one node at the center and spreads the
rest around it on a ring, with edges meeting each shape's real border.

For a hub that is itself a polygon (`hex`, `diamond`, `polyN`), spokes should
leave from the **faces** of the polygon — evenly distributed along the flat
sides — so a hexagon bus gets one clean connection per side instead of a fan of
lines all meeting at one point. This is the "polygon-face docking" from
[`docs/RECOMMENDATIONS.md`](../../RECOMMENDATIONS.md).

## What changes

Add a `radial` instruction that arranges members around a hub:

```fl
radial hub=<id> [radius=<r>] [start=<deg>] [dock] [gap=<g>]
```

- `hub=<id>` (required) — node id placed at the center.
- `radius=<r>` — ring radius in pixels; default derived from hub size + `gap`.
- `start=<deg>` — starting angle for the first spoke (default `-90`, i.e. 12
  o'clock), spokes laid out clockwise.
- `dock` — when the hub is a polygon, dock each spoke to a **face** of the hub
  (evenly split across sides) instead of ray-casting from the center.
- `gap=<g>` — clearance between the hub border and the ring; also feeds the
  default radius.

Members are the **non-hub top-level items** (standalone nodes and groups) in
declaration order; they are placed evenly on the ring. A single member sits at
`start`. Edges attach to real shape borders as usual.

- An unknown or missing `hub=` warns and the diagram falls back to the default
  stack (no radial).
- An unknown attribute value (non-numeric `radius`/`start`/`gap`) warns and is
  ignored.
- `dock` on a non-polygon hub warns and is ignored (ray-cast is used).

When **no** `radial` instruction is present, existing behavior (stack, or layered
when `layer`s exist) is unchanged.

## Out of scope (later changes)

- Auto-deriving the hub from edges (change 0011)
- Multi-ring / spiral placement, weighted angles
- Mixing radial with `layer` columns in one diagram (radial wins if both present)

## Requirements touched

Folds into [`../../spec.md`](../../spec.md):
- Language: `radial hub=... [radius=] [start=] [dock] [gap=]` instruction.

## Example + docs (required)

- New example `examples/hub.fl` — a core bus with producers and consumers docked
  to a hexagon hub.
- Committed as `docs/img/hub.svg` **and** `docs/img/hub.png`; embedded in
  `docs/gallery.md`.
- `reference/language.md` — `radial` section.

## Impact

- `src/flowlite/model.py` — add `Radial` dataclass; add `radial` to `Diagram`.
- `src/flowlite/parser.py` — parse the `radial` instruction + validation.
- `src/flowlite/shapes/geometry.py` — add `dock_anchor` (polygon-face anchor).
- `src/flowlite/layout/radial.py` — new engine (ring + docking).
- `src/flowlite/compiler.py` — choose engine: radial > layered > stack.
- Tests: `tests/test_radial.py`, render/golden.

## Open questions

- Default `start`: `-90` (12 o'clock, chosen) vs `0` (3 o'clock)?
- Should a diagram with only a hub (no members) warn or render a lone node?
