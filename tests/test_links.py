"""Interactive link tests (change 0009)."""

from __future__ import annotations

from pathlib import Path

from flowlite.compiler import compile_diagram
from flowlite.parser import parse
from flowlite.themes import load_theme

EXAMPLES = Path(__file__).resolve().parents[1] / "examples"
GOLDEN = Path(__file__).resolve().parent / "golden"
THEME = load_theme("midnight")


# --- Parser ---------------------------------------------------------------


def test_link_parsed_verbatim():
    diagram, warnings = parse('node a "A" link=../../examples/hello.fl')
    assert warnings == []
    assert diagram.nodes[0].link == "../../examples/hello.fl"


def test_absolute_url_parsed():
    diagram, warnings = parse('node a "A" link=https://example.com/x')
    assert warnings == []
    assert diagram.nodes[0].link == "https://example.com/x"


def test_absent_link_is_empty():
    diagram, warnings = parse('node a "A"')
    assert warnings == []
    assert diagram.nodes[0].link == ""


def test_empty_link_warns_and_ignored():
    diagram, warnings = parse('node a "A" link=')
    assert diagram.nodes[0].link == ""
    assert any("empty link" in w for w in warnings)


# --- Render ---------------------------------------------------------------


def test_linked_node_is_wrapped_in_anchor():
    svg = compile_diagram('node a "A" link=https://example.com')
    assert '<a href="https://example.com"' in svg
    assert "</a>" in svg


def test_link_has_target_and_rel():
    svg = compile_diagram('node a "A" link=https://example.com')
    assert 'target="_blank"' in svg
    assert 'rel="noopener noreferrer"' in svg


def test_plain_node_has_no_anchor():
    svg = compile_diagram('node a "A"')
    assert "<a " not in svg


def test_href_is_escaped():
    # A URL with a query string containing & must be escaped in the attribute.
    svg = compile_diagram('node a "A" link=https://example.com/x?a=1&b=2')
    assert "&amp;b=2" in svg


def test_link_wraps_shape_and_label():
    svg = compile_diagram('node a "Click me" link=https://example.com')
    start = svg.index('<a href="https://example.com"')
    end = svg.index("</a>")
    window = svg[start:end]
    assert ">Click me<" in window  # the label is inside the anchor


def test_relative_link_kept():
    svg = compile_diagram('node a "A" link=../../examples/hello.fl')
    assert 'href="../../examples/hello.fl"' in svg


# --- Determinism ----------------------------------------------------------


def test_links_are_deterministic():
    source = 'node a "A" link=https://x\nnode b "B" link=https://y\nedge a -> b'
    assert compile_diagram(source, THEME) == compile_diagram(source, THEME)


# --- Golden ---------------------------------------------------------------


def test_golden_index():
    source = (EXAMPLES / "index.fl").read_text(encoding="utf-8")
    expected = (GOLDEN / "index.svg").read_text(encoding="utf-8")
    assert compile_diagram(source, THEME) == expected


def test_no_link_sources_unchanged():
    for name in ("hello", "shapes", "hub", "schema"):
        source = (EXAMPLES / f"{name}.fl").read_text(encoding="utf-8")
        expected = (GOLDEN / f"{name}.svg").read_text(encoding="utf-8")
        assert compile_diagram(source, THEME) == expected
