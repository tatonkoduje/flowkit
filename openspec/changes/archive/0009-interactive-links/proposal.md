# Change 0009 — Interactive links

- **Status:** draft
- **Type:** feature
- **Owner:** maintainers
- **Depends on:** [0001](../archive/0001-walking-skeleton/proposal.md), [0008](../archive/0008-icons/proposal.md)

## Why

A diagram is often a **map**: each box is a doorway to more detail — a source
file, a service dashboard, a runbook, another diagram. Today a node is inert.
Honoring `link=<url>` turns any node into a **hyperlink**: the whole shape and its
label become clickable in any SVG viewer, so one picture becomes an index into
many.

Following the project's minimal-surface rule, this is a **rendering-only** change:
`link=` changes how a node is emitted, not how it is measured or placed, so it
composes with every existing feature and leaves all current output byte-identical
when unused.

## What changes

Honor the `link=<url>` node attribute:

```fl
node pipeline "Layered layout" kind=service icon=layers link=../../examples/pipeline.fl
```

- `link=<url>` wraps the node — its shape **and** label — in an SVG
  `<a href="...">` so it is clickable and keyboard-focusable.
- The URL is copied verbatim into `href` (relative links, `#anchors`, `https://…`
  all work); it is **XML-escaped** like any other user text.
- A node with no `link=` renders exactly as before.
- The `link` value is the raw token after `link=`; an empty value (`link=`) warns
  and is ignored.

Because FlowLite is dependency-free and offline, links are never validated by
fetching — the author is responsible for their targets. A `link` that is not a
plausible URL (contains whitespace after unquoting) warns and is ignored.

## Out of scope (later changes)

- Links on groups, tables or edges
- `target=`/`rel=` attributes, tooltips, hover styles
- Multi-target nodes, clickable regions inside a table

## Requirements touched

Folds into [`../../spec.md`](../../spec.md):
- Language: `link=<url>` node attribute; nodes render as SVG hyperlinks.

## Example + docs (required)

- New example `examples/index.fl` — an **index** of the other examples: one node
  per diagram, each linking to its `.fl` source (and/or its gallery SVG), so the
  index is a navigable table of contents.
- Committed as `docs/img/index.svg` **and** `docs/img/index.png`; embedded in
  `docs/gallery.md`.
- `reference/language.md` — `link=` row in the `node` table + an Interactive
  subsection; drop `link=` from "tolerated but ignored".

## Impact

- `src/flowlite/model.py` — add `link: str = ""` to `Node`.
- `src/flowlite/parser.py` — parse `link=<url>`; warn on an empty/invalid value.
- `src/flowlite/render/svg.py` — wrap a linked node's fragments in `<a href>`.
- Tests: `tests/test_links.py`; golden `index.svg`.

## Open questions

- Wrap only the shape+label (chosen) vs draw an invisible click rect over the box?
- Warn on empty `link=` (chosen) vs silently ignore?
