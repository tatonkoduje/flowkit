# Design — 0010 PNG export

## One function, many tools

```python
def svg_to_png(svg_path: Path, png_path: Path,
               scale: float = 2.0, width: int | None = None) -> str | None:
    """Export SVG to PNG with the first available converter.

    Returns the converter name on success, or None when none is installed.
    """
```

Converters, tried in this fixed order (deterministic, first hit wins):

| converter | detection | sizing |
|---|---|---|
| `rsvg-convert` | `shutil.which` | `-z <scale>` or `-w <width>` |
| `resvg` | `which` | `--zoom <scale>` or `--width <width>` |
| `inkscape` | `which` | `-w <width>` (px); scale via `-w` from the SVG width |
| `chromium` / `google-chrome` | `which` | `--headless --screenshot --window-size=W,H` |
| `sips` (macOS) | `which` | `--resampleWidth <width>` |
| `qlmanage` (macOS) | `which` | `-s <maxdim>` thumbnail |

Argument forms:

```python
("rsvg-convert", ["-o", png, *size_rsvg, svg])
("resvg",        [*size_resvg, svg, png])
("inkscape",     [svg, "--export-type=png", f"--export-filename={png}", *size_ink])
("chromium",     [chrome, "--headless", "--disable-gpu", "--no-sandbox",
                  f"--screenshot={png}", f"--window-size={w},{h}", f"file://{svg}"])
("sips",         ["-s", "format", "png", svg, "--out", png, *size_sips])
("qlmanage",     ["-t", "-s", str(maxdim), "-o", outdir, svg])  # then rename
```

Sizing rules:
- `rsvg-convert`: scale → `-z`; width → `-w`.
- `resvg`: scale → `--zoom`; width → `--width`.
- `inkscape`: width → `-w` (px). For scale, multiply the SVG's declared width by
  `scale` (read `width="…"` from the SVG header) — needs no extra tool.
- `chromium`: width → `--window-size=w,?` where the height comes from the SVG's
  declared height times `width/svg_width`; scale multiplies both.
- `sips`: width → `--resampleWidth`; scale → `--resampleWidth` = svg_width*scale.
- `qlmanage`: `-s` max dimension; only scale maps (svg_width*scale), width maps to
  `max(width, svg_height_scaled)`.

The SVG's intrinsic width/height are read once from the document
(`width="123"`), so the sizing math is concrete and deterministic.

## CLI

```
flowlite <input.fl> [-o OUT.svg] [--png] [--png-scale N] [--png-width W]
```

- `--png-scale N` default `2.0`; `--png-width W` optional.
- Giving both is a usage error (`argparse` mutual-exclusion group) → exit `2`.
- `--png-scale`/`--png-width` without `--png` warns that they are ignored
  (they only affect PNG export).

Flow:

1. Always write the SVG (unchanged).
2. If `--png`: `name = svg_to_png(out, png, scale, width)`.
   - `name` → print `wrote <png> (via <name>)`.
   - `None` → print an install hint to stderr; **exit 0** (SVG succeeded).

## Determinism & purity

PNG bytes come from an external tool, so they are **not** byte-guaranteed — that
is why PNG stays out of golden tests (only the SVG is a golden contract). The
compiler core is untouched and still imports nothing third-party.

## Tests (fake converter, no real tools)

Create a fake `rsvg-convert` shell script in `tmp_path` that records its args to
a file and writes a 1×1 PNG, prepend `tmp_path` to `PATH` for the test, then:

- `svg_to_png(...)` returns `"rsvg-convert"` and forwards `-z`/`-w`.
- `main([..., "--png"])` returns `0`, writes the `.png`, and prints the converter.
- With an empty `PATH` (converter absent): `main` still returns `0`, writes the
  SVG, and stderr mentions a converter.
- `--png-scale` with `--png-width` → exit `2` (argparse) and no SVG.

`shutil.which`/`subprocess.run` are also patchable, but a real fake script on
`PATH` exercises the true code path (which is the point).
