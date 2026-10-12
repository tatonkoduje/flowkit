"""Shape measurement + geometry tests."""

from __future__ import annotations

import math

from flowlite import shapes
from flowlite.measure import measure_node, poly_sides
from flowlite.model import Node
from flowlite.themes import load_theme

THEME = load_theme("midnight")


def _node(shape: str, label: str = "X") -> Node:
    return measure_node(Node(id="n", label=label, shape=shape), THEME)


def test_poly_sides_parsing_and_clamp():
    assert poly_sides("poly5") == 5
    assert poly_sides("poly12") == 12
    assert poly_sides("poly3") == 3
    assert poly_sides("poly99") == 12
    assert poly_sides("poly0") == 3
    assert poly_sides("polynomial") == 6  # fallback


def test_card_measure():
    n = _node("card", "Hello")
    assert n.height == THEME.node_height
    assert n.width >= 150.0


def test_db_is_taller_than_card():
    assert _node("db").height > _node("card").height


def test_hub_is_square():
    n = _node("hub")
    assert n.width == n.height


def test_polygon_is_square():
    n = _node("poly6")
    assert n.width == n.height


def test_diamond_measure():
    n = _node("diamond", "Decision")
    assert n.height == 96.0
    assert n.width > _node("card", "Decision").width


def test_polygon_vertices_count():
    for sides in (3, 5, 6, 8, 12):
        n = _node(f"poly{sides}")
        assert len(shapes.polygon_vertices(n)) == sides


def test_anchor_on_circle_for_hub():
    n = _with_position(_node("hub"), 0, 0)
    cx, cy = shapes.center(n)
    ax, ay = shapes.anchor(n, cx + 1000, cy)  # straight east
    assert math.isclose(ax, cx + n.width / 2 + 4.0, abs_tol=1e-6)
    assert math.isclose(ay, cy, abs_tol=1e-6)


def test_anchor_on_rectangle_border_for_card():
    n = _with_position(_node("card"), 0, 0)
    cx, _cy = shapes.center(n)
    ax, _ay = shapes.anchor(n, 1000, n.height / 2)
    assert math.isclose(ax, cx + n.width / 2 + 4.0, abs_tol=1e-6)


def test_vertical_anchor_top_and_bottom_center():
    n = _with_position(_node("card"), 10, 20)
    bx, by = shapes.vertical_anchor(n, bottom=True)
    tx, ty = shapes.vertical_anchor(n, bottom=False)
    assert math.isclose(bx, n.x + n.width / 2)
    assert math.isclose(by, n.y + n.height)
    assert math.isclose(ty, n.y)


def test_vertical_anchor_polygon_uses_apothem():
    n = _with_position(_node("poly8"), 0, 0)
    _, by = shapes.vertical_anchor(n, bottom=True)
    cy = n.y + n.height / 2
    apothem = (n.width / 2) * math.cos(math.pi / 8)
    assert math.isclose(by, cy + apothem, abs_tol=1e-6)


def test_hex_vertices_match_full_box():
    n = _with_position(_node("hex", "Gateway"), 0, 0)
    verts = shapes.hex_vertices(n)
    xs = [x for x, _ in verts]
    ys = [y for _, y in verts]
    # The drawn hexagon spans the node's full width and height.
    assert math.isclose(min(xs), n.x)
    assert math.isclose(max(xs), n.x + n.width)
    assert math.isclose(min(ys), n.y)
    assert math.isclose(max(ys), n.y + n.height)


def test_hex_vertical_anchor_on_flat_edge():
    n = _with_position(_node("hex"), 10, 20)
    _, by = shapes.vertical_anchor(n, bottom=True)
    tx, ty = shapes.vertical_anchor(n, bottom=False)
    assert math.isclose(by, n.y + n.height, abs_tol=1e-6)
    assert math.isclose(ty, n.y, abs_tol=1e-6)


def test_hex_anchor_stays_on_drawn_border():
    n = _with_position(_node("hex"), 0, 0)
    cx, cy = shapes.center(n)
    # A ray to the lower-right must meet the slanted right edge, not an interior
    # point of an inscribed regular hexagon.
    ax, ay = shapes.anchor(n, cx + 1000, cy + 1000)
    assert n.x - 4.0 <= ax <= n.x + n.width + 4.0
    assert n.y - 4.0 <= ay <= n.y + n.height + 4.0
    assert ax > cx and ay > cy


def _with_position(node: Node, x: float, y: float) -> Node:
    from dataclasses import replace

    return replace(node, x=x, y=y)
