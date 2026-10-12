# Design — 0003 Edge styling

## Model

`Edge` gains four optional fields (all with defaults, so existing sources are
unaffected):

```python
@dataclass(frozen=True)
class Edge:
    src: str
    dst: str
    label: str = ""
    style: str = "normal"   # normal | dashed | bold
    arrow: str = "normal"   # normal | dot | none
    curve: str = "bezier"   # bezier | straight
```

## Parser

The existing `EDGE_RE` captures the trailing remainder; we extend it to pull a
quoted label first, then scan `key=value` tokens (order-independent), reusing a
small attribute scanner. Unknown values warn + fall back, matching shapes.

## Rendering

- **Markers** (in `<defs>`): keep `#arrow` (triangle). Add `#arrow-dot`
  (circle). `arrow=none` emits no `marker-end`.
- **Stroke style**: `dashed` → `stroke-dasharray="7 5"`; `bold` → width `3.4`
  (vs `2.2`).
- **Curve**: `bezier` uses the current control points; `straight` emits a line
  between the two anchors.
- **Label**: computed at the path midpoint. For bezier we use the cubic midpoint
  `(p0 + 3c1 + 3c2 + p3)/8`; for straight, the segment midpoint. A rounded pill
  (`theme.label_background`) is drawn behind the text (`theme.label_text`).

## Theme

`Theme` already parses `labelBackground`/`labelText` in the JSON but does not
expose them; add `label_background`/`label_text` fields.

## Determinism

Attribute order does not affect output (we normalize into fields). Markers and
`<defs>` are emitted in fixed order. Labels render in edge declaration order.

## Test strategy

- Parser: label + each attribute parsed; unknown values warn + default; order of
  attributes does not matter.
- Render: `dashed` emits `stroke-dasharray`; `bold` emits width `3.4`; `dot`
  references `#arrow-dot`; `none` has no `marker-end`; `straight` emits `L`
  (line) not `C`; a label emits `<rect ... rx=` pill + text; label text escaped.
- Golden: `flow.fl`.
