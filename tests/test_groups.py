"""Group parsing, measurement, layout and rendering tests (change 0004)."""

from __future__ import annotations

from pathlib import Path

from flowlite.compiler import compile_diagram
from flowlite.layout.stack import layout
from flowlite.measure import measure
from flowlite.parser import parse
from flowlite.themes import load_theme

EXAMPLES = Path(__file__).resolve().parents[1] / "examples"
GOLDEN = Path(__file__).resolve().parent / "golden"
THEME = load_theme("midnight")


def _pipeline(source: str):
    diagram, warnings = parse(source)
    return measure(diagram, THEME), warnings


# --- Parser ---------------------------------------------------------------


def test_group_parsed():
    diagram, warnings = parse('group core "Core" kind=service')
    assert warnings == []
    assert len(diagram.groups) == 1
    g = diagram.groups[0]
    assert g.id == "core"
    assert g.title == "Core"
    assert g.kind == "service"


def test_group_default_kind():
    diagram, _ = parse('group core "Core"')
    assert diagram.groups[0].kind == "default"


def test_node_in_attaches_membership():
    diagram, warnings = parse('group core "Core"\nnode a "A" in=core')
    assert warnings == []
    assert diagram.nodes[0].group == "core"


def test_unknown_group_warns_and_detaches():
    diagram, warnings = parse('node a "A" in=ghost')
    assert diagram.nodes[0].group == ""
    assert any("unknown group 'ghost'" in w for w in warnings)


# --- Measurement ----------------------------------------------------------


def test_group_sized_to_contain_members():
    diagram, _ = _pipeline(
        'group core "Core"\n'
        'node a "A" in=core\n'
        'node b "B" in=core\n'
        'node c "C" in=core'
    )
    g = diagram.groups[0]
    members = [n for n in diagram.nodes if n.group == "core"]
    assert len(members) == 3
    for m in members:
        assert g.width >= m.width
        assert g.height >= m.height


def test_empty_group_gets_minimum_frame():
    diagram, _ = _pipeline('group core "Core"')
    g = diagram.groups[0]
    assert g.width == 220.0
    assert g.height == 110.0


# --- Layout ---------------------------------------------------------------


def test_members_excluded_from_toplevel():
    diagram, _ = _pipeline(
        'group core "Core"\n'
        'node a "A" in=core\n'
        'node standalone "S"\n'
        'node b "B" in=core'
    )
    positioned, _w, _h = layout(diagram, THEME)
    # Group placed once; standalone node also placed.
    assert len(positioned.groups) == 1
    assert {n.id for n in positioned.nodes} == {"a", "standalone", "b"}


def test_frame_strictly_contains_members():
    diagram, _ = _pipeline(
        'group core "Core" kind=service\n'
        'node a "A" in=core\n'
        'node b "B" in=core\n'
        'node c "C" in=core\n'
        'node d "D" in=core'
    )
    positioned, _w, _h = layout(diagram, THEME)
    g = positioned.groups[0]
    members = [n for n in positioned.nodes if n.group == "core"]
    assert len(members) == 4
    for m in members:
        assert m.x >= g.x
        assert m.y >= g.y
        assert m.x + m.width <= g.x + g.width
        assert m.y + m.height <= g.y + g.height


def test_layout_is_deterministic():
    source = (EXAMPLES / "layers.fl").read_text(encoding="utf-8")
    d1, _ = _pipeline(source)
    d2, _ = _pipeline(source)
    l1, _w1, _h1 = layout(d1, THEME)
    l2, _w2, _h2 = layout(d2, THEME)
    assert l1 == l2


# --- Rendering ------------------------------------------------------------


def _compile(source: str) -> str:
    return compile_diagram(source, THEME)


def test_frame_emitted_before_nodes():
    svg = _compile('group core "Core" kind=service\nnode a "A" kind=service in=core')
    body = svg[svg.index("</defs>") :]
    frame = body.index('stroke-dasharray="7 6"')
    node = body.index('fill="url(#g-service)"')
    assert frame < node


def test_group_title_rendered():
    svg = _compile('group core "Core Services" kind=service\nnode a "A" in=core')
    assert ">CORE SERVICES<" in svg


def test_edge_can_target_group():
    svg = _compile(
        'group a "A" kind=web\n'
        'node n "N" in=a\n'
        'group b "B" kind=service\n'
        'node m "M" in=b\n'
        'edge a -> b "req"'
    )
    assert svg.count("marker-end") == 1


def test_group_title_is_escaped():
    svg = _compile('group g "A & B" kind=service\nnode a "A" in=g')
    assert "A &amp; B" in svg


def test_no_groups_still_renders():
    svg = _compile('node a "A"')
    assert 'stroke-dasharray="7 6"' not in svg


# --- Golden ---------------------------------------------------------------


def test_golden_layers():
    source = (EXAMPLES / "layers.fl").read_text(encoding="utf-8")
    expected = (GOLDEN / "layers.svg").read_text(encoding="utf-8")
    assert _compile(source) == expected
