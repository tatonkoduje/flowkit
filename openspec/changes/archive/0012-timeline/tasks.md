# Tasks — 0012 Timeline (Gantt-style)

## 1. Model

- [x] 1.1 `model.py`: add `Marker`, `TimelineSection`, `TimelineItem`, `Timeline`;
      add `timeline: Timeline | None` to `Diagram`.
- [x] 1.2 Tests: dataclasses construct; a `Diagram` with a timeline round-trips.

## 2. Parser

- [x] 2.1 Parse `timeline "T" ["S"] [from <date>] [to <date>]`.
- [x] 2.2 Parse `section "Title" [color=]`.
- [x] 2.3 Parse `bar "label" START -> END [section=] [color=] [state=] [note=]`.
- [x] 2.4 Parse `milestone "label" DATE [section=] [color=] [note=]`.
- [x] 2.5 Parse `axis <unit> [grid <unit>]` and `marker <date> ["label"]`.
- [x] 2.6 ISO `date` parsing; warnings: outside a timeline, unknown section,
      `end < start` (swap), unknown state/axis/grid, timeline+graph mix.
- [x] 2.7 Tests: every instruction parsed; every warning.

## 3. Theme

- [x] 3.1 Add a `timeline` block (background, bands, grid, axis, text, milestone,
      palette) to `themes/midnight.json` and `themes/light.json`.
- [x] 3.2 `themes.py`: load the `timeline` block (optional; sensible defaults).
- [x] 3.3 Tests: block parses; missing block falls back.

## 4. Layout

- [x] 4.1 `layout/timeline.py`: range resolution (explicit or derived), date→x,
      sections→rows, items→boxes, axis/grid tick positions, marker x.
- [x] 4.2 Tests: monotonic x; derived range; sections in declaration order;
      single-day bar min width; milestone centred.

## 5. Render

- [x] 5.1 `render/timeline.py`: background, bands, grid, gutter titles, bars,
      milestones, labels/notes, axis, markers, title.
- [x] 5.2 Escape all text; reuse `_defs` (gradients/shadow).
- [x] 5.3 Tests: title/sections/labels/notes present + escaped; `done` vs
      `active` fills differ; marker at date x.

## 6. Compiler

- [x] 6.1 Dispatch to the timeline renderer when `diagram.timeline` is set.
- [x] 6.2 Graph examples unchanged (no timeline).

## 7. Tests + golden

- [x] 7.1 `tests/test_timeline.py`.
- [x] 7.2 Golden `tests/golden/timeline.svg`; existing goldens unchanged.

## 8. Example + docs (required)

- [x] 8.1 `examples/timeline.fl` — a delivery timeline (sections, marker, grid,
      bars, milestones, mixed states).
- [x] 8.2 Commit `docs/img/timeline.svg` **and** `docs/img/timeline.png`; embed in
      `docs/gallery.md`.
- [x] 8.3 `reference/language.md` — full `timeline` section.
- [x] 8.4 `openspec/spec.md` — Timeline requirements.
- [x] 8.5 `docs/getting-started.md` — a "non-graph diagrams" note.

## 9. Close out

- [x] 9.1 Archive this change; add it to `changes/README.md`; CHANGELOG.

## Definition of done

- `timeline.fl` renders a Gantt with coloured phase rows, a start marker, weekly
  gridlines, a month axis, half-height single-day bars and milestone diamonds —
  no warnings.
- Tests + ruff green; golden + determinism green; graph examples byte-identical.
- Gallery (svg+png), reference, spec and getting-started updated; change archived.
