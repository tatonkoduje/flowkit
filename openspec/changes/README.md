# Change sequence

FlowLite is built **one small change at a time**. Each change is a self-contained
proposal that can be reviewed, implemented and tested in isolation. Nothing spans
more than one concern.

## Golden rule: every change ships an example and docs

A change is **not done** until it has, in addition to code and tests:

1. **A new (or extended) example** under `examples/`, compiled and committed to
   the gallery as **both** `docs/img/<name>.svg` and `docs/img/<name>.png`. The
   SVG is the readable vector output (opens in IDE/browser); the PNG is for
   pasting into documents.
2. **Documentation updated** to match the change:
   - [`../spec.md`](../spec.md) — requirements.
   - [`../../reference/language.md`](../../reference/language.md) — new keywords/attributes.
   - [`../../docs/gallery.md`](../../docs/gallery.md) — the rendered example.
   - [`../../docs/getting-started.md`](../../docs/getting-started.md) — if the
     first-run experience changes.

This keeps the docs **alive and human-facing**: getting-started, a language
reference and a gallery that grow with the tool instead of lagging behind it.
The docs are a **deliverable, not an afterthought**.

## Roadmap

| # | Change | Scope | Example it adds | Status |
|---|---|---|---|---|
| 0001 | [walking-skeleton](archive/0001-walking-skeleton/proposal.md) | title/theme/node/edge, `card`, stack layout, SVG, themes, CLI | `hello.fl` — vertical card chain | done |
| 0002 | [shapes](archive/0002-shapes/proposal.md) | `db`, `hub`, `hex`, `pill`, `diamond`, `polyN` + anchoring | `shapes.fl` — every shape once | done |
| 0003 | [edge styling](archive/0003-edge-styling/proposal.md) | labels, `dashed`/`bold`, `bezier`/`straight`, arrow=`dot`/`none` | `flow.fl` — labelled/typed edges | done |
| 0004 | [groups](archive/0004-groups/proposal.md) | translucent frames + member grid, group edge anchoring | `layers.fl` — services in frames | done |
| 0005 | [layered layout](archive/0005-layered-layout/proposal.md) | `layer` columns | `pipeline.fl` — left→right pipeline | done |
| 0006 | [radial layout](archive/0006-radial-layout/proposal.md) | `radial hub=` + `dock` onto polygon faces | `hub.fl` — core + modules | done |
| 0007 | [tables](archive/0007-tables/proposal.md) | `table` + `col:`/`row:` | `schema.fl` — table nodes | done |
| 0008 | [icons](archive/0008-icons/proposal.md) | curated lucide set, tinted by `kind` | extend existing examples with icons | done |
| 0009 | [interactive](archive/0009-interactive-links/proposal.md) | `link=` clickable nodes | `index.fl` → links between examples | done |
| 0010 | [png](archive/0010-png-export/proposal.md) | hardened best-effort PNG export (+ sizing) | (regenerates gallery PNGs) | done |
| 0011 | [auto-layout](archive/0011-auto-layout/proposal.md) | directed (Sugiyama-style) engine | `auto.fl` — same source, auto-placed | done |
| 0012 | [timeline](archive/0012-timeline/proposal.md) | Gantt-style `timeline`: sections, bars, milestones, axis/grid, markers, colours | `timeline.fl` — delivery schedule | done |
| 0013 | [timeline spacing](archive/0013-timeline-spacing/proposal.md) | `week=` / `width=` to stretch the timeline x-axis | extends `timeline.fl` | done |
| 0014 | [timeline leading grid](archive/0014-timeline-grid-lead/proposal.md) | grid covers the area before the start marker | extends `timeline.fl` | done |
| 0015 | [timeline axis align](archive/0015-timeline-axis-align/proposal.md) | axis ticks bounded by the plot + a full leading week of grid | extends `timeline.fl` | done |

Order is a guide, not a contract — changes may be reordered or split, but each
one stays small and independently testable, and each still ships an example + docs.

## Lifecycle

1. Write `proposal.md` (+ `design.md`, `tasks.md`) in `changes/<id>/`, including
   the **example** and **doc updates** it will add.
2. Review: is it small? does it fit the principles in `AGENTS.md`?
3. Implement, keeping `tasks.md` checked off as you go.
4. Add the example, render it, update the docs (see the golden rule).
5. Fold requirements into [`../spec.md`](../spec.md).
6. Remove the change folder (or move it to `archive/` if you prefer a history).

## Documentation map (human-facing)

| Document | Purpose | Grows with |
|---|---|---|
| [`../../README.md`](../../README.md) | landing page, quick start | every change |
| [`../../docs/getting-started.md`](../../docs/getting-started.md) | first diagram, compiling | 0001, first-run changes |
| [`../../reference/language.md`](../../reference/language.md) | the DSL reference | every language change |
| [`../../docs/gallery.md`](../../docs/gallery.md) | rendered examples | every change |
| [`../../docs/RECOMMENDATIONS.md`](../../docs/RECOMMENDATIONS.md) | design rationale | rarely |
