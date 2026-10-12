"""Radial layout tests (change 0006)."""

from __future__ import annotations

import math
from pathlib import Path

from flowlite import shapes
from flowlite.compiler import compile_diagram
from flowlite.layout import radial
from flowlite.measure import measure
from flowlite.parser import parse
from flowlite.themes import load_theme

EXAMPLES = Path(__file__).resolve().parents[1] / "examples"
GOLDEN = Path(__file__).resolve().parent / "golden"
THEME = load_theme("midnight")


def _diagram(source: str):
    diagram, warnings = parse(source)
    return measure(diagram, THEME), warnings


# --- Parser ---------------------------------------------------------------


def test_radial_head_parsed():
    diagram, warnings = parse('node a "A"\nnode b "B"\nradial hub=a')
    assert warnings == []
    assert diagram.radial is not None
    assert diagram.radial.hub == "a"
    assert diagram.radial.radius is None
    assert diagram.radial.start == -90.0
    assert diagram.radial.gap == 70.0
    assert diagram.radial.dock is False


def test_radial_attrs_parsed():
    diagram, warnings = parse(
        'node a "A" shape=hex\nradial hub=a radius=260 start=0 gap=40 dock'
    )
    assert warnings == []
    assert diagram.radial.radius == 260.0
    assert diagram.radial.start == 0.0
    assert diagram.radial.gap == 40.0
    assert diagram.radial.dock is True


def test_radial_missing_hub_warns():
    diagram, warnings = parse('node a "A"\nradial radius=200')
    assert diagram.radial is None
    assert any("requires hub" in w for w in warnings)


def test_radial_unknown_hub_warns_and_dropped():
    diagram, warnings = parse('node a "A"\nradial hub=ghost')
    assert diagram.radial is None
    assert any("hub 'ghost' is not a node" in w for w in warnings)


def test_radial_bad_numeric_warns():
    diagram, warnings = parse('node a "A"\nradial hub=a radius=abc')
    assert diagram.radial is not None
    assert diagram.radial.radius is None
    assert any("radius is not a number" in w for w in warnings)


def test_radial_dock_needs_polygon_hub():
    diagram, warnings = parse('node a "A" shape=card\nradial hub=a dock')
    assert diagram.radial is not None
    assert diagram.radial.dock is False
    assert any("dock needs a polygon hub" in w for w in warnings)


def test_radial_dock_kept_for_hex():
    diagram, warnings = parse('node a "A" shape=hex\nradial hub=a dock')
    assert warnings == []
    assert diagram.radial.dock is True


def test_second_radial_ignored():
    diagram, warnings = parse(
        'node a "A"\nnode b "B"\nradial hub=a\nradial hub=b'
    )
    assert diagram.radial.hub == "a"
    assert any("already declared" in w for w in warnings)


# --- Layout ---------------------------------------------------------------


def _ring_source(n: int) -> str:
    nodes = "\n".join(f'node n{i} "N{i}"' for i in range(n))
    return f'node hub "HUB" shape=hub\n{nodes}\nradial hub=hub'


def test_hub_is_centered():
    diagram, _ = _diagram(_ring_source(4))
    positioned, w, h = radial.layout(diagram, THEME)
    hub = next(n for n in positioned.nodes if n.id == "hub")
    center_x = hub.x + hub.width / 2
    center_y = hub.y + hub.height / 2
    assert abs(center_x - w / 2) < 0.51
    assert abs(center_y - h / 2) < 40.0


def test_members_are_equidistant_from_hub():
    diagram, _ = _diagram(_ring_source(5))
    positioned, _w, _h = radial.layout(diagram, THEME)
    lookup = {n.id: n for n in positioned.nodes}
    hub = lookup["hub"]
    hx, hy = hub.x + hub.width / 2, hub.y + hub.height / 2
    dists = []
    for i in range(5):
        m = lookup[f"n{i}"]
        mx, my = m.x + m.width / 2, m.y + m.height / 2
        dists.append(math.hypot(mx - hx, my - hy))
    assert max(dists) - min(dists) < 0.51


def test_single_member_sits_at_start():
    diagram, _ = _diagram('node hub "HUB"\nnode only "ONLY"\nradial hub=hub start=-90 radius=200')
    positioned, _w, _h = radial.layout(diagram, THEME)
    lookup = {n.id: n for n in positioned.nodes}
    hub = lookup["hub"]
    hx, hy = hub.x + hub.width / 2, hub.y + hub.height / 2
    m = lookup["only"]
    mx, my = m.x + m.width / 2, m.y + m.height / 2
    # start=-90 -> directly above the hub.
    assert my < hy
    assert abs(mx - hx) < 0.51


def test_radius_override_respected():
    diagram, _ = _diagram(
        'node hub "HUB"\nnode a "A"\nnode b "B"\nradial hub=hub radius=500'
    )
    positioned, _w, _h = radial.layout(diagram, THEME)
    lookup = {n.id: n for n in positioned.nodes}
    hub = lookup["hub"]
    hx, hy = hub.x + hub.width / 2, hub.y + hub.height / 2
    for node_id in ("a", "b"):
        m = lookup[node_id]
        mx, my = m.x + m.width / 2, m.y + m.height / 2
        assert abs(math.hypot(mx - hx, my - hy) - 500.0) < 0.51


def test_group_member_stays_in_frame():
    diagram, _ = _diagram(
        'node hub "HUB"\n'
        'group g "G" kind=service\n'
        'node a "A" in=g\n'
        'node b "B" in=g\n'
        'radial hub=hub'
    )
    positioned, _w, _h = radial.layout(diagram, THEME)
    g = positioned.groups[0]
    members = [n for n in positioned.nodes if n.group == "g"]
    assert len(members) == 2
    for m in members:
        assert g.x <= m.x and m.x + m.width <= g.x + g.width
        assert g.y <= m.y and m.y + m.height <= g.y + g.height


def test_radial_is_deterministic():
    source = (EXAMPLES / "hub.fl").read_text(encoding="utf-8")
    d1, _ = _diagram(source)
    d2, _ = _diagram(source)
    l1, _w1, _h1 = radial.layout(d1, THEME)
    l2, _w2, _h2 = radial.layout(d2, THEME)
    assert l1 == l2


# --- Geometry (docking) ---------------------------------------------------


def test_dock_anchor_on_polygon_edge():
    diagram, _ = _diagram('node h "H" shape=hex\nradial hub=h')
    hub = next(n for n in measure(diagram, THEME).nodes if n.id == "h")
    x, y = shapes.dock_anchor(hub, hub.x + hub.width / 2, hub.y - 1000)
    # Point sits on the hexagon border, not the centroid.
    cx, cy = shapes.center(hub)
    assert math.hypot(x - cx, y - cy) > 1.0


def test_dock_anchor_non_polygon_falls_back():
    diagram, _ = _diagram('node h "H"\nradial hub=h')
    hub = next(n for n in measure(diagram, THEME).nodes if n.id == "h")
    got = shapes.dock_anchor(hub, hub.x + hub.width / 2, hub.y - 1000)
    expected = shapes.anchor(hub, hub.x + hub.width / 2, hub.y - 1000)
    assert got == expected


def test_opposite_spokes_dock_to_different_faces():
    diagram, _ = _diagram('node h "H" shape=hex\nradial hub=h')
    hub = next(n for n in measure(diagram, THEME).nodes if n.id == "h")
    cx, cy = shapes.center(hub)
    up = shapes.dock_anchor(hub, cx, cy - 1000)
    down = shapes.dock_anchor(hub, cx, cy + 1000)
    assert up != down
    assert up[1] < cy < down[1]


def test_dock_anchor_on_drawn_hex_border():
    diagram, _ = _diagram('node h "H" shape=hex\nradial hub=h')
    hub = next(n for n in measure(diagram, THEME).nodes if n.id == "h")
    cx, cy = shapes.center(hub)
    # A spoke to the lower-right must land on the slanted right edge of the
    # wide hexagon the renderer draws, not inside it.
    x, y = shapes.dock_anchor(hub, cx + 1000, cy + 1000)
    assert hub.x - 4.0 <= x <= hub.x + hub.width + 4.0
    assert hub.y - 4.0 <= y <= hub.y + hub.height + 4.0
    assert x > cx and y > cy


def test_dock_is_deterministic_and_on_border():
    diagram, _ = _diagram('node h "H" shape=hex\nradial hub=h')
    hub = next(n for n in measure(diagram, THEME).nodes if n.id == "h")
    cx, cy = shapes.center(hub)
    p1 = shapes.dock_anchor(hub, cx + 900, cy - 400)
    p2 = shapes.dock_anchor(hub, cx + 900, cy - 400)
    assert p1 == p2
    assert hub.x - 4.0 <= p1[0] <= hub.x + hub.width + 4.0
    assert hub.y - 4.0 <= p1[1] <= hub.y + hub.height + 4.0


# --- Compiler engine selection -------------------------------------------


def test_no_radial_leaves_stack_unchanged():
    source = (EXAMPLES / "hello.fl").read_text(encoding="utf-8")
    expected = (GOLDEN / "hello.svg").read_text(encoding="utf-8")
    assert compile_diagram(source, THEME) == expected


def test_no_radial_leaves_layered_unchanged():
    source = (EXAMPLES / "pipeline.fl").read_text(encoding="utf-8")
    expected = (GOLDEN / "pipeline.svg").read_text(encoding="utf-8")
    assert compile_diagram(source, THEME) == expected


def test_radial_used_when_declared():
    svg = compile_diagram('node a "A" shape=hub\nnode b "B"\nradial hub=a')
    assert svg.startswith("<svg")
    assert ">A<" in svg and ">B<" in svg


# --- Golden ---------------------------------------------------------------


def test_golden_hub():
    source = (EXAMPLES / "hub.fl").read_text(encoding="utf-8")
    expected = (GOLDEN / "hub.svg").read_text(encoding="utf-8")
    assert compile_diagram(source, THEME) == expected
