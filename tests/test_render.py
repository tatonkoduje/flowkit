"""Rendering + determinism + escaping tests."""

from __future__ import annotations

from pathlib import Path

from flowlite.compiler import compile_diagram
from flowlite.themes import load_theme

EXAMPLES = Path(__file__).resolve().parents[1] / "examples"
GOLDEN = Path(__file__).resolve().parent / "golden"


def _compile(source: str) -> str:
    return compile_diagram(source, load_theme("midnight"))


def test_output_is_valid_svg_envelope():
    svg = _compile('title "T"\nnode a "A"')
    assert svg.startswith("<svg")
    assert svg.rstrip().endswith("</svg>")
    assert 'viewBox="0 0' in svg


def test_all_nodes_rendered():
    svg = _compile('node a "A" kind=web\nnode b "B"\nnode c "C"')
    assert svg.count("<rect x=") == 3
    assert ">A<" in svg and ">B<" in svg and ">C<" in svg


def test_db_renders_ellipse():
    svg = _compile('node a "A" shape=db')
    assert "<ellipse" in svg


def test_hub_renders_circle():
    svg = _compile('node a "A" shape=hub')
    assert "<circle" in svg


def test_hex_and_polygon_render_polygon():
    assert "<polygon" in _compile('node a "A" shape=hex')
    assert "<polygon" in _compile('node a "A" shape=poly6')
    assert "<polygon" in _compile('node a "A" shape=diamond')


def test_edges_rendered():
    svg = _compile('node a "A"\nnode b "B"\nedge a -> b')
    assert svg.count("marker-end") == 1


def test_edge_to_unknown_node_is_skipped():
    svg = _compile('node a "A"\nedge a -> ghost')
    assert svg.count("marker-end") == 0


def test_dashed_style():
    svg = _compile('node a "A"\nnode b "B"\nedge a -> b style=dashed')
    assert 'stroke-dasharray="7 5"' in svg


def test_bold_style():
    svg = _compile('node a "A"\nnode b "B"\nedge a -> b style=bold')
    assert 'stroke-width="3.4"' in svg


def test_dot_arrow():
    svg = _compile('node a "A"\nnode b "B"\nedge a -> b arrow=dot')
    assert "url(#arrow-dot)" in svg


def test_no_arrow():
    svg = _compile('node a "A"\nnode b "B"\nedge a -> b arrow=none')
    assert "marker-end" not in svg


def test_straight_curve_emits_line():
    svg = _compile('node a "A"\nnode b "B"\nedge a -> b curve=straight')
    assert 'd="M ' in svg and " L " in svg


def test_edge_label_renders_pill_and_text():
    svg = _compile('node a "A"\nnode b "B"\nedge a -> b "payload"')
    assert 'rx="13"' in svg
    assert ">payload<" in svg


def test_edge_label_is_escaped():
    svg = _compile('node a "A"\nnode b "B"\nedge a -> b "A & B"')
    assert "A &amp; B" in svg


def test_golden_flow():
    source = (EXAMPLES / "flow.fl").read_text(encoding="utf-8")
    expected = (GOLDEN / "flow.svg").read_text(encoding="utf-8")
    assert _compile(source) == expected


def test_text_is_escaped():
    svg = _compile('node a "A < B & C > D"')
    assert "A &lt; B &amp; C &gt; D" in svg
    assert "A < B" not in svg


def test_deterministic_output():
    source = (EXAMPLES / "hello.fl").read_text(encoding="utf-8")
    assert _compile(source) == _compile(source)


def test_golden_hello():
    source = (EXAMPLES / "hello.fl").read_text(encoding="utf-8")
    expected = (GOLDEN / "hello.svg").read_text(encoding="utf-8")
    assert _compile(source) == expected


def test_golden_shapes():
    source = (EXAMPLES / "shapes.fl").read_text(encoding="utf-8")
    expected = (GOLDEN / "shapes.svg").read_text(encoding="utf-8")
    assert _compile(source) == expected


def test_golden_kitchen_sink():
    source = (EXAMPLES / "kitchen-sink.fl").read_text(encoding="utf-8")
    expected = (GOLDEN / "kitchen-sink.svg").read_text(encoding="utf-8")
    assert _compile(source) == expected
