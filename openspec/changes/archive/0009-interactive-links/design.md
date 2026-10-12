# Design — 0009 Interactive links

## Model

`Node` gains `link: str = ""`. Default empty → the node renders exactly as today,
so every existing golden is byte-identical.

## Parser

`NODE_LINK_RE = re.compile(r"\blink=(\S+)")`. On a node line:

- `link=` present with a non-empty token → `link = token`.
- `link=` present with an empty value (`link=` at end / `link=`) → warn
  `empty link, ignored`, `link=""`.
- absent → `link=""`.

The token is taken **verbatim** (no unquoting): URLs are relative paths or
`https://…` and rarely contain spaces; whitespace terminates the token, which is
the desired behavior for a dotted attribute. The empty case is detected by
comparing against the generic attribute scan so `link=` alone is caught.

## Rendering

The node is a sequence of fragments (body + icon + label). When `node.link` is
set, those fragments are wrapped in a single anchor group:

```
<a href="<escaped url>" target="_blank" rel="noopener noreferrer">
  ... shape body, icon, label ...
</a>
```

- `target="_blank"` + `rel="noopener noreferrer"` open the target in a new tab —
  the safe default for embedded SVG (avoids navigating away from the viewer).
- The `href` is XML-escaped with the existing `esc()` helper.
- Grouping the shape **and** the label means the entire node box is clickable
  (SVG hit-tests the drawn geometry, so the whole card is the target).

Wrapping is done once, in `_node`, around the returned fragment list, so every
shape path benefits without touching each branch:

```python
def _node(node, theme) -> list[str]:
    parts = _node_body(node, theme)   # existing logic
    if node.link:
        return [_open_link(node.link), *parts, "</a>"]
    return parts
```

The current `_node` returns early for each shape; refactor it so the shape logic
lives in `_node_body` and `_node` does the (optional) anchor wrap. This is a
mechanical, contained refactor.

## Determinism

`href` is fixed text; wrapping adds a constant open/close around the same
fragments. Same source → byte-identical SVG. A node without `link=` skips the
wrapper entirely (no empty `<a>`).

## Interaction with other features

- **Icons (0008):** the icon fragment is inside the same wrap (clickable).
- **Edges:** edges are drawn separately and are **not** linked — only the node is.
  An edge still attaches to the node border normally.
- **Tables/groups:** out of scope; `link=` on them is ignored.

## Test strategy

- Parser: `link=https://x` kept; `link=../../examples/pipeline.fl` kept verbatim;
  empty `link=` warns and is ignored; absent → empty.
- Render: a linked node emits `<a href="...">` wrapping the shape and label;
  a plain node emits no `<a>`; the `href` is XML-escaped; `target`/`rel` present.
- Determinism: compiling twice is byte-identical.
- Golden: `index.fl`; all other goldens unchanged (no `link=`).
