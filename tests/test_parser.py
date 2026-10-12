"""Parser tests for the 0001 subset."""

from __future__ import annotations

from flowlite.parser import parse


def test_defaults():
    diagram, warnings = parse("")
    assert diagram.title == "Diagram"
    assert diagram.subtitle == ""
    assert diagram.theme == "midnight"
    assert diagram.nodes == ()
    assert diagram.edges == ()
    assert warnings == []


def test_title_and_subtitle():
    diagram, _ = parse('title "Main" "Sub"')
    assert diagram.title == "Main"
    assert diagram.subtitle == "Sub"


def test_title_without_subtitle():
    diagram, _ = parse('title "Main"')
    assert diagram.title == "Main"
    assert diagram.subtitle == ""


def test_theme():
    diagram, _ = parse("theme light")
    assert diagram.theme == "light"


def test_nodes_keep_declaration_order():
    diagram, _ = parse('node a "A" kind=web\nnode b "B"')
    assert [n.id for n in diagram.nodes] == ["a", "b"]
    assert diagram.nodes[0].kind == "web"
    assert diagram.nodes[1].kind == "default"


def test_shape_parsed():
    diagram, warnings = parse('node a "A" shape=db')
    assert warnings == []
    assert diagram.nodes[0].shape == "db"


def test_polyn_shape_parsed():
    diagram, _ = parse('node a "A" shape=poly8')
    assert diagram.nodes[0].shape == "poly8"


def test_unknown_shape_warns_and_falls_back():
    diagram, warnings = parse('node a "A" shape=banana')
    assert diagram.nodes[0].shape == "card"
    assert len(warnings) == 1
    assert "banana" in warnings[0]


def test_unknown_attributes_are_tolerated():
    diagram, warnings = parse('node a "A" icon=globe kind=store shape=db')
    assert warnings == []
    assert len(diagram.nodes) == 1
    assert diagram.nodes[0].kind == "store"


def test_edges():
    diagram, _ = parse("edge a -> b")
    assert len(diagram.edges) == 1
    assert diagram.edges[0].src == "a"
    assert diagram.edges[0].dst == "b"


def test_edge_with_label_and_style():
    diagram, warnings = parse('edge a -> b "payload" style=dashed')
    assert warnings == []
    assert diagram.edges[0].src == "a"
    assert diagram.edges[0].label == "payload"
    assert diagram.edges[0].style == "dashed"


def test_edge_label_parsed():
    diagram, warnings = parse('edge a -> b "unified feed"')
    assert warnings == []
    assert diagram.edges[0].label == "unified feed"


def test_edge_attributes_parsed_in_any_order():
    diagram, warnings = parse('edge a -> b "l" curve=straight style=bold arrow=dot')
    edge = diagram.edges[0]
    assert warnings == []
    assert (edge.style, edge.arrow, edge.curve) == ("bold", "dot", "straight")


def test_edge_defaults():
    diagram, _ = parse("edge a -> b")
    edge = diagram.edges[0]
    assert edge.label == ""
    assert (edge.style, edge.arrow, edge.curve) == ("normal", "normal", "bezier")


def test_edge_unknown_values_warn_and_default():
    diagram, warnings = parse("edge a -> b style=wavy arrow=rocket")
    edge = diagram.edges[0]
    assert edge.style == "normal"
    assert edge.arrow == "normal"
    assert len(warnings) == 2


def test_comments_and_blank_lines():
    diagram, warnings = parse("# comment\n\n   \nnode a \"A\"\n")
    assert len(diagram.nodes) == 1
    assert warnings == []


def test_unknown_line_warns_and_continues():
    diagram, warnings = parse('node a "A"\nfrobnicate x\nnode b "B"')
    assert len(diagram.nodes) == 2
    assert len(warnings) == 1
    assert "cannot parse" in warnings[0]
