# Design — 0008 Icons

## Icon data (vendored, ISC, lucide subset)

`icons/lucide.json`:

```json
{
  "meta": {"set": "lucide", "license": "ISC", "viewBox": "0 0 24 24"},
  "icons": {
    "database": "M12 2C7.6 2 4 3.3 4 5s3.6 3 8 3 ...",
    "server": "...",
    ...
  }
}
```

Each value is the **path `d`** of a 24×24 stroke icon (lucide is stroke-based:
`fill="none"`, `stroke="currentColor"`, `stroke-width="2"`, round caps/joins).
Curated set (≈20 glyphs used across the examples):

| name | use |
|---|---|
| `database` | stores |
| `server` | services |
| `cloud` | external systems |
| `globe` | web / internet |
| `network` | gateways, buses |
| `git-branch` | decisions / pipelines |
| `user` | users |
| `users` | groups of users |
| `shield` | security |
| `lock` | auth |
| `key` | keys |
| `message-square` | events / messages |
| `layers` | stacks |
| `credit-card` | payments |
| `shopping-cart` | orders |
| `activity` | analytics / metrics |
| `bell` | notifications |
| `file-text` | documents |
| `box` | generic container |
| `cpu` | compute |
| `hard-drive` | storage |
| `zap` | queues / fast paths |

Every glyph is stored **verbatim** from lucide (ISC); a `meta.license` field
records attribution, satisfying the "vendor, don't depend" rule.

## Loader

```python
# src/flowlite/icons.py
def all_icons() -> dict[str, str]: ...      # name -> path d
def icon_path(name: str) -> str | None: ... # None if unknown
```

Reads `icons/lucide.json` (path relative to the repo root, like `themes.py`),
cached in a module-level variable. No third-party imports.

## Model

`Node` gains `icon: str = ""`. Default empty → no icon (back-compatible; every
existing golden is unchanged).

## Parser

`NODE_ICON_RE = re.compile(r"\bicon=(\w[\w-]*)")`. On a node line:

- `icon=` present and the name is in `icons.all_icons()` → keep it.
- present but unknown → warn `unknown icon '<name>', ignored`, `icon=""`.
- absent → `icon=""`.

Group/table `icon=` is out of scope (ignored, as today).

## Rendering

Draw the icon inside the node, tinted white like the label, with a fixed box of
`ICON_SIZE = 22` at 24×24 viewBox (stroke-width scaled to keep ~2px).

- **Card / db / pill / hex / diamond** (wide, text-centered shapes): draw the
  icon to the **left of the label** and shift the label right by
  `ICON_SIZE + ICON_GAP`. When an icon is present, the label is centered in the
  remaining box to the right of the icon, so text stays balanced.
- **hub / polyN** (compact, center-text): draw the icon **above** the label,
  nudging the label down, so a hexagon/polygon keeps a centered stack.

The icon is emitted as:

```
<g transform="translate(x,y) scale(s)" fill="none" stroke="#FFFFFF"
   stroke-opacity="0.92" stroke-width="2" stroke-linecap="round"
   stroke-linejoin="round"><path d="..."/></g>
```

Label placement helper `_label(...)` gains an optional `dx`/`dy` and the node
draw functions decide icon position from `shape`.

Because icon geometry depends only on the node box and constants, output stays
deterministic.

## Measurement interaction

Icons do **not** change measurement in this change (the node box stays the same;
the label shifts within it). This keeps every payload width identical and avoids
re-measuring wide labels — a smaller, safer diff. (If a label plus icon overflows,
text is simply centered in the remaining space; acceptable for the curated set.)

## Determinism

Icon path data is fixed in the JSON; no randomness. The same node → identical
`<path>` bytes.

## Test strategy

- Loader: the set is non-empty; `icon_path` returns a string for a known name and
  `None` for an unknown one.
- Parser: `icon=database` kept; unknown `icon=ghost` warns and clears the icon;
  no icon → `icon=""`.
- Render: a node with `icon=database` emits a `<path>` inside a translated/stroked
  group; a node without an icon emits none; the icon group is tinted white.
- Golden: extended examples regenerate; all other goldens unchanged (no icons).
- Determinism: compiling twice is byte-identical.
