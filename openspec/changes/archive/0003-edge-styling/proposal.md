# Change 0003 — Edge styling

- **Status:** draft
- **Type:** feature
- **Owner:** maintainers
- **Depends on:** [0001](../archive/0001-walking-skeleton/proposal.md), [0002](../archive/0002-shapes/proposal.md)

## Why

Edges carry meaning: what flows, how it flows, and in which direction. Today an
edge is a bare arrow. Labels and styles are what turn a picture of boxes into a
readable architecture — e.g. `"unified feed"` over a solid arrow, `"results"`
on a dashed one.

## What changes

Extend `edge` with a label and three attributes:

```fl
edge <from> -> <to> "label" style=<style> arrow=<arrow> curve=<curve>
```

| Attribute | Values | Default |
|---|---|---|
| label | quoted string | *(none)* |
| `style=` | `normal`, `dashed`, `bold` | `normal` |
| `arrow=` | `normal`, `dot`, `none` | `normal` |
| `curve=` | `bezier`, `straight` | `bezier` |

- Labels render on a pill at the midpoint of the edge.
- `dashed` uses a dash pattern; `bold` a thicker stroke.
- `dot` ends with a round terminator; `none` has no head.
- `straight` draws a line; `bezier` a smooth curve.

Unknown values fall back to the default and warn (same convention as shapes).

## Out of scope (later changes)

- Multiple labels / label positioning
- Orthogonal routing, self-loops, ports
- Colored edges

## Requirements touched

Folds into [`../../spec.md`](../../spec.md):
- Language: `edge` gains label, `style=`, `arrow=`, `curve=`.
- Rendering: dashed/bold strokes, arrow head variants, straight/bezier curves,
  edge label pills.

## Example + docs (required)

- New example `examples/flow.fl` — labelled, typed edges.
- Committed as `docs/img/flow.svg` **and** `docs/img/flow.png`; embedded in
  `docs/gallery.md`.
- `reference/language.md` — the `edge` table.

## Impact

- `src/flowlite/model.py` — add `label`, `style`, `arrow`, `curve` to `Edge`.
- `src/flowlite/parser.py` — parse the label and the three attributes.
- `src/flowlite/render/svg.py` — markers for heads/dots, dash/bold, curve/straight,
  label pill; theme gains label pill colors.
- `themes/*.json` — `labelBackground`/`labelText` already present; expose them.
- Tests: `tests/test_parser.py`, `tests/test_render.py`, golden.

## Open questions

- Label pill uses theme `labelBackground`/`labelText` — good enough?
- `bold` = thicker `normal` stroke (no separate meaning) — acceptable?
