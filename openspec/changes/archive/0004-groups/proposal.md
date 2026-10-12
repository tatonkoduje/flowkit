# Change 0004 — Groups

- **Status:** draft
- **Type:** feature
- **Owner:** maintainers
- **Depends on:** [0001](../archive/0001-walking-skeleton/proposal.md), [0002](../archive/0002-shapes/proposal.md)

## Why

Architectures have boundaries: a cluster, a bounded context, a layer. A
translucent frame around a set of nodes makes those boundaries visible and lets
an edge target the whole group. This is what turns a flat list of boxes into a
structured picture.

## What changes

- Add `group <id> "Title" [kind=]` — a translucent background frame.
- Add `in=<group>` to `node` so a node becomes a member of a group.
- Lay members out automatically in a grid inside the frame.
- Frame is drawn **under** the nodes, with a title label and a dashed border in
  the group's kind color.
- An `edge` may reference a **group id**, anchoring to the frame border.

`shape=` for groups (polygon/penta frames) is **out of scope** here — this change
is the rectangular frame only.

## Out of scope (later changes)

- Polygonal / penta group frames (with `layer`/`radial`)
- Nested groups
- Group `scale=`

## Requirements touched

Folds into [`../../spec.md`](../../spec.md):
- Language: `group` instruction; `node ... in=`.
- Rendering: translucent group frames drawn under nodes; group title.

## Example + docs (required)

- New example `examples/layers.fl` — a few services grouped into frames.
- Committed as `docs/img/layers.svg` **and** `docs/img/layers.png`; embedded in
  `docs/gallery.md`.
- `reference/language.md` — `group` section + `in=` on `node`.

## Impact

- `src/flowlite/model.py` — add `Group` dataclass; add `group: str` to `Node`;
  add `groups` to `Diagram`.
- `src/flowlite/parser.py` — parse `group` and `in=`.
- `src/flowlite/measure.py` — size groups from their members.
- `src/flowlite/layout/stack.py` — place members in a grid inside their group;
  top-level layout treats a group as one item.
- `src/flowlite/render/svg.py` — draw frames before edges/nodes; group title;
  group edge anchoring.
- Tests: `tests/test_groups.py`, render + golden.

## Open questions

- Grid: 2 columns when a group has more than one member (FlowKit behavior)?
- Group frame color: use the group's `kind` first color, low opacity (as FlowKit)?
