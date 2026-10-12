"""CLI tests."""

from __future__ import annotations

import os
import stat
from pathlib import Path

from flowlite.__main__ import main, svg_to_png


def test_version(capsys):
    import pytest

    with pytest.raises(SystemExit) as exc:
        main(["--version"])
    assert exc.value.code == 0
    assert "flowlite" in capsys.readouterr().out


def test_missing_input_returns_nonzero(tmp_path):
    assert main([str(tmp_path / "nope.fl")]) == 1


def test_compiles_to_svg(tmp_path):
    src = tmp_path / "d.fl"
    src.write_text('title "T"\nnode a "A"\nnode b "B"\nedge a -> b\n', encoding="utf-8")
    out = tmp_path / "out" / "d.svg"
    rc = main([str(src), "-o", str(out)])
    assert rc == 0
    assert out.exists()
    assert out.read_text(encoding="utf-8").startswith("<svg")


def test_unknown_theme_returns_nonzero(tmp_path, capsys):
    src = tmp_path / "d.fl"
    src.write_text('theme nope\nnode a "A"\n', encoding="utf-8")
    rc = main([str(src), "-o", str(tmp_path / "d.svg")])
    assert rc == 1
    assert "nope" in capsys.readouterr().err


# --- PNG export (change 0010) --------------------------------------------


def _fake_converter(dir_path: Path, name: str = "rsvg-convert") -> Path:
    """A tiny executable that records its args and produces a stub PNG."""
    script = dir_path / name
    script.write_text(
        "#!/bin/sh\n"
        f'printf "%s\\n" "$@" >> "{dir_path}/args.txt"\n'
        # Find the output -o value and write a 1x1 PNG-ish file there.
        'for ((i=1;i<=$#;i++)); do :; done\n'
        'out=""\n'
        'prev=""\n'
        'for a in "$@"; do\n'
        '  if [ "$prev" = "-o" ]; then out="$a"; fi\n'
        '  prev="$a"\n'
        "done\n"
        '[ -n "$out" ] && printf "\\211PNG\\r\\n\\032\\n" > "$out"\n'
        "exit 0\n",
        encoding="utf-8",
    )
    script.chmod(script.stat().st_mode | stat.S_IEXEC)
    return script


def test_svg_to_png_uses_first_converter(tmp_path):
    _fake_converter(tmp_path)
    svg = tmp_path / "d.svg"
    svg.write_text('<svg width="100" height="50"></svg>', encoding="utf-8")
    png = tmp_path / "d.png"
    env_path = str(tmp_path)
    old = os.environ["PATH"]
    os.environ["PATH"] = env_path + os.pathsep + old
    try:
        name = svg_to_png(svg, png)
    finally:
        os.environ["PATH"] = old
    assert name == "rsvg-convert"
    assert png.exists()
    args = (tmp_path / "args.txt").read_text(encoding="utf-8")
    assert "-z" in args  # default scale flag forwarded


def test_svg_to_png_width_flag(tmp_path):
    _fake_converter(tmp_path)
    svg = tmp_path / "d.svg"
    svg.write_text('<svg width="100" height="50"></svg>', encoding="utf-8")
    png = tmp_path / "d.png"
    old = os.environ["PATH"]
    os.environ["PATH"] = str(tmp_path) + os.pathsep + old
    try:
        svg_to_png(svg, png, scale=2.0, width=320)
    finally:
        os.environ["PATH"] = old
    args = (tmp_path / "args.txt").read_text(encoding="utf-8")
    assert "-w" in args and "320" in args


def test_png_cli_reports_converter(tmp_path, capsys):
    _fake_converter(tmp_path)
    src = tmp_path / "d.fl"
    src.write_text('node a "A"\n', encoding="utf-8")
    old = os.environ["PATH"]
    os.environ["PATH"] = str(tmp_path) + os.pathsep + old
    try:
        rc = main([str(src), "-o", str(tmp_path / "d.svg"), "--png"])
    finally:
        os.environ["PATH"] = old
    assert rc == 0
    assert (tmp_path / "d.png").exists()
    assert "rsvg-convert" in capsys.readouterr().out


def test_png_no_converter_is_best_effort(tmp_path, capsys):
    src = tmp_path / "d.fl"
    src.write_text('node a "A"\n', encoding="utf-8")
    out = tmp_path / "d.svg"
    old = os.environ["PATH"]
    os.environ["PATH"] = str(tmp_path)  # empty of converters
    try:
        rc = main([str(src), "-o", str(out), "--png"])
    finally:
        os.environ["PATH"] = old
    assert rc == 0  # SVG still written; PNG is best effort
    assert out.exists()
    assert "converter" in capsys.readouterr().err.lower()


def test_png_scale_and_width_conflict(tmp_path):
    import pytest

    src = tmp_path / "d.fl"
    src.write_text('node a "A"\n', encoding="utf-8")
    out = tmp_path / "d.svg"
    with pytest.raises(SystemExit) as exc:
        main([str(src), "-o", str(out), "--png", "--png-scale", "3", "--png-width", "500"])
    assert exc.value.code == 2
    assert not out.exists()

