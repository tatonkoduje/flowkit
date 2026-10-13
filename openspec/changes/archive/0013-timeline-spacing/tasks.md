# Tasks — 0013 Timeline spacing

## 1. Model

- [x] 1.1 `model.py`: add `week: float | None` and `width: int | None` to
      `Timeline`.

## 2. Parser

- [x] 2.1 Parse `week=<px>` and `width=<px>` on the `timeline` header.
- [x] 2.2 Warnings: non-numeric / `<= 0` ignored; both given → `width` wins.
- [x] 2.3 Tests: parsed; `week=0`/`week=abc` warn; both → width wins; defaults None.

## 3. Layout

- [x] 3.1 `layout/timeline.py`: use `timeline.width` if set, else
      `week` (default `WEEK_PX`) × weeks.
- [x] 3.2 Tests: bigger `week` → wider chart; `width=` exact; proportional;
      dates stay in the plot; defaults unchanged.

## 4. Tests + golden

- [x] 4.1 Extend `tests/test_timeline.py` (parser + layout).
- [x] 4.2 Regenerate golden `tests/golden/timeline.svg` (now `week=72`); other
      goldens unchanged.

## 5. Example + docs (required)

- [x] 5.1 Add `week=72` to `examples/timeline.fl`.
- [x] 5.2 Re-commit `docs/img/timeline.svg` **and** `docs/img/timeline.png`.
- [x] 5.3 `reference/language.md` — `week=` / `width=` rows + a note.
- [x] 5.4 `openspec/spec.md` — Timeline sizing requirement.

## 6. Close out

- [x] 6.1 Archive this change; add it to `changes/README.md`; CHANGELOG.

## Definition of done

- `week=` widens the x-axis (longer gaps between weeks); `width=` pins the total
  width; both documented and tested; defaults byte-identical.
- Tests + ruff green; golden + determinism green.
- Gallery (svg+png), reference and spec updated; change archived.
