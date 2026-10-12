# Change 0008 — Icons

- **Status:** draft
- **Type:** feature
- **Owner:** maintainers
- **Depends on:** [0001](../archive/0001-walking-skeleton/proposal.md), [0002](../archive/0002-shapes/proposal.md), [0007](../archive/0007-tables/proposal.md)

## Why

A shape and a color tell the reader *what kind* of thing a box is; an **icon**
tells them at a glance. A database with a cylinder glyph, a queue with a stack
glyph, a gateway with a network glyph — icons are the fastest visual cue in a
diagram. Today `icon=` is parsed and thrown away.

Following [recommendation 4](../../RECOMMENDATIONS.md) — *aesthetics as data* —
the icon set is **vendored as data** (SVG path data in a file), not code. It is a
small, curated subset of [lucide](https://lucide.dev) (ISC), so output stays
dependency-free and every glyph is deterministic.

## What changes

Honor the `icon=<name>` node attribute:

```fl
node db "PostgreSQL" kind=store shape=db icon=database
```

- `icon=<name>` names an icon in the vendored set.
- The icon is drawn **inside the node**, tinted to match the kind (white, like the
  label), and the label shifts to make room.
- An **unknown** icon name warns and is ignored (the node renders without an
  icon) — consistent with unknown shapes/kinds.
- No `icon=` → no icon; output is byte-identical to today for existing sources.

The set ships as `icons/lucide.json`: a map of `name → 24×24 path data`. A tiny
loader (`icons.py`) reads it; unknown names are reported by the parser at parse
time against the loaded set.

## Out of scope (later changes)

- Icons on edges, groups, tables or in cell text
- Icon-only nodes (no label), icon scaling beyond the default size
- Project-local / user-supplied icon files, multi-path icons with fills

## Requirements touched

Folds into [`../../spec.md`](../../spec.md):
- Language: `icon=<name>` node attribute; vendored, data-driven icon set.

## Example + docs (required)

- Extend existing examples with icons (`hello.fl`, `shapes.fl`, `hub.fl`,
  `schema.fl`) — each keeps its shape; icons are additive.
- Re-commit affected `docs/img/*.svg` **and** `.png`; gallery captions mention icons.
- `reference/language.md` — `icon=` row in the `node` table + an Icons subsection
  listing the vendored names.

## Impact

- `icons/lucide.json` — vendored path data (new).
- `src/flowlite/icons.py` — loader + `icon_path(name)` (new).
- `src/flowlite/model.py` — add `icon: str = ""` to `Node`.
- `src/flowlite/parser.py` — parse `icon=<name>`; warn on unknown names.
- `src/flowlite/render/svg.py` — draw the icon (tinted) and offset the label.
- Tests: `tests/test_icons.py`; goldens for the extended examples.

## Open questions

- Icon placement for non-card shapes (db/hex/poly): left-of-label (chosen) vs
  centered above the label?
- Warn on unknown icon (chosen) vs silently ignore?
