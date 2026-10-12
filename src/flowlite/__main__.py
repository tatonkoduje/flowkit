"""FlowLite command-line entry point.

Usage:
    PYTHONPATH=src python3 -m flowlite <input.fl> [-o OUTPUT.svg]
        [--png] [--png-scale N | --png-width W]
"""

from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
from pathlib import Path

from . import __version__
from .compiler import compile_diagram
from .parser import parse_file
from .themes import ThemeError

#: Install hint shown when no SVG->PNG converter is found.
_CONVERTER_HINT = (
    "no SVG->PNG converter found (install one, e.g. `brew install librsvg`)"
)

_SVG_SIZE_RE = re.compile(r'<svg[^>]*\bwidth="(\d+)"[^>]*\bheight="(\d+)"')


def svg_intrinsic_size(svg_path: Path) -> tuple[int, int]:
    """Read the SVG's declared pixel width/height; default (1000, 700)."""
    try:
        head = svg_path.read_text(encoding="utf-8")[:400]
    except OSError:
        return 1000, 700
    m = _SVG_SIZE_RE.search(head)
    if m:
        return int(m.group(1)), int(m.group(2))
    return 1000, 700


def _run(cmd: list[str]) -> bool:
    try:
        subprocess.run(cmd, check=True)
        return True
    except (OSError, subprocess.CalledProcessError):
        return False


def svg_to_png(
    svg_path: Path,
    png_path: Path,
    scale: float = 2.0,
    width: int | None = None,
) -> str | None:
    """Export ``svg_path`` to ``png_path`` with the first available converter.

    Returns the converter name on success, or ``None`` when none is installed (or
    the chosen one failed). Best effort: never raises for a missing tool.
    """
    sw, sh = svg_intrinsic_size(svg_path)
    target_w = width if width is not None else max(1, round(sw * scale))

    # rsvg-convert
    if shutil.which("rsvg-convert"):
        size = ["-w", str(target_w)] if width is not None else ["-z", str(scale)]
        if _run(["rsvg-convert", "-o", str(png_path), *size, str(svg_path)]):
            return "rsvg-convert"

    # resvg
    if shutil.which("resvg"):
        size = ["--width", str(target_w)] if width is not None else ["--zoom", str(scale)]
        if _run(["resvg", *size, str(svg_path), str(png_path)]):
            return "resvg"

    # inkscape
    if shutil.which("inkscape"):
        if _run(
            [
                "inkscape",
                str(svg_path),
                "--export-type=png",
                f"--export-filename={png_path}",
                f"--export-width={target_w}",
            ]
        ):
            return "inkscape"

    # chromium / google-chrome (headless)
    for chrome in ("chromium", "chromium-browser", "google-chrome", "google-chrome-stable"):
        if shutil.which(chrome):
            target_h = max(1, round(sh * target_w / sw))
            if _run(
                [
                    chrome,
                    "--headless",
                    "--disable-gpu",
                    "--no-sandbox",
                    f"--screenshot={png_path}",
                    f"--window-size={target_w},{target_h}",
                    f"file://{svg_path.resolve()}",
                ]
            ):
                return chrome

    # sips (macOS)
    if shutil.which("sips"):
        if _run(
            ["sips", "-s", "format", "png", str(svg_path), "--out", str(png_path),
             "--resampleWidth", str(target_w)]
        ):
            return "sips"

    # qlmanage (macOS fallback)
    if shutil.which("qlmanage"):
        target_h = max(1, round(sh * target_w / sw))
        outdir = png_path.parent
        if _run(
            ["qlmanage", "-t", "-s", str(max(target_w, target_h)), "-o", str(outdir),
             str(svg_path)]
        ):
            produced = Path(str(svg_path) + ".png")
            if produced.exists():
                produced.replace(png_path)
                return "qlmanage"

    return None


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="flowlite",
        description="FlowLite — compile a .fl source into a styled SVG.",
    )
    parser.add_argument("input", help="source .fl file")
    parser.add_argument(
        "-o",
        "--output",
        help="output .svg path (default: build/<input>.svg)",
    )
    parser.add_argument(
        "--png",
        action="store_true",
        help="also export a PNG next to the SVG (best effort)",
    )
    size = parser.add_mutually_exclusive_group()
    size.add_argument(
        "--png-scale",
        type=float,
        default=2.0,
        help="PNG scale factor (default: 2)",
    )
    size.add_argument(
        "--png-width",
        type=int,
        default=None,
        help="PNG pixel width (overrides --png-scale)",
    )
    parser.add_argument("--version", action="version", version=f"flowlite {__version__}")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_arg_parser().parse_args(argv)

    src = Path(args.input)
    if not src.exists():
        print(f"flowlite: input not found: {src}", file=sys.stderr)
        return 1

    source = src.read_text(encoding="utf-8")
    _diagram, warnings = parse_file(src)
    for warning in warnings:
        print(f"flowlite: warning: {warning}", file=sys.stderr)

    try:
        svg_text = compile_diagram(source)
    except ThemeError as exc:
        print(f"flowlite: {exc}", file=sys.stderr)
        return 1

    out = Path(args.output) if args.output else Path("build") / src.with_suffix(".svg").name
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(svg_text, encoding="utf-8")
    print(f"flowlite: wrote {out}")

    if args.png_scale != 2.0 or args.png_width is not None:
        if not args.png:
            print(
                "flowlite: --png-scale/--png-width only apply with --png",
                file=sys.stderr,
            )

    if args.png:
        png = out.with_suffix(".png")
        name = svg_to_png(out, png, args.png_scale, args.png_width)
        if name:
            print(f"flowlite: wrote {png} (via {name})")
        else:
            print(f"flowlite: {_CONVERTER_HINT}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
