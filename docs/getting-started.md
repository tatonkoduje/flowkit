# Getting started

FlowLite turns a small text file into a **beautiful SVG diagram**.

> **Status:** early. The first slice (change 0001) supports a minimal
> subset — `title`, `theme`, `node`, `edge` and one shape (`card`). This guide
> grows with the tool; see [`gallery.md`](gallery.md) for what is possible today.

## Requirements

- **Python 3.10+** — nothing else. FlowLite uses the standard library only.

Optional, for PNG export: `rsvg-convert` (`brew install librsvg`), Inkscape, or
macOS `qlmanage`. FlowLite shells out to whichever is installed; SVG is always
written regardless.

## Your first diagram

Create `hello.fl`:

```fl
title "Hello FlowLite" "three cards, gradients, arrows"
theme midnight

node web "Web app" kind=web
node api "API"     kind=gateway
node db  "Storage" kind=store

edge web -> api
edge api -> db
```

Compile it:

```bash
PYTHONPATH=src python3 -m flowlite hello.fl -o build/hello.svg --png
```

Open `build/hello.svg` in a browser. You should see three gradient cards stacked
vertically with arrows between them.

## Output formats

FlowLite writes **SVG by default** — it is the primary output, opens in any IDE
or browser, and is what you commit alongside diagrams. PNG is optional:

```bash
PYTHONPATH=src python3 -m flowlite hello.fl            # -> build/hello.svg
PYTHONPATH=src python3 -m flowlite hello.fl --png      # -> build/hello.svg + build/hello.png
```

SVG export never depends on anything installed; PNG needs `rsvg-convert`,
Inkscape or macOS `qlmanage` (if none is present, the SVG is still written and a
message is printed).

## How it works

```
.fl text ──parse──▶ model ──measure──▶ sized ──layout──▶ positioned ──render──▶ SVG
```

Every stage is a pure function, so the same source always renders identically.

## Next steps

- [Language reference](../reference/language.md) — every instruction.
- [Gallery](gallery.md) — rendered examples.
- [Recommendations](RECOMMENDATIONS.md) — where FlowLite is going.

## Troubleshooting

- **`No module named flowlite`** — the package lives in `src/`; run with
  `PYTHONPATH=src`.
- **A line was ignored** — the parser prints a warning to stderr for unparseable
  lines. Strings use double quotes.
