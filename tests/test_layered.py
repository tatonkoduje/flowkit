"""Layered layout tests (change 0005)."""

from __future__ import annotations

from pathlib import Path

from flowlite.compiler import compile_diagram
from flowlite.layout import layered
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


def test_layer_parsed_with_ids():
    diagram, warnings = parse(
        'node a "A"\nnode b "B"\nnode c "C"\nlayer 1: a b c'
    )
    assert warnings == []
    assert len(diagram.layers) == 1
    assert diagram.layers[0].index == 1
    assert diagram.layers[0].ids == ("a", "b", "c")


def test_two_layers_kept_in_declaration_order():
    diagram, _ = parse('node a "A"\nnode b "B"\nlayer 2: b\nlayer 1: a')
    assert [layer.index for layer in diagram.layers] == [2, 1]


def test_empty_layer_warns():
    diagram, warnings = parse("layer 1:")
    assert diagram.layers == ()
    assert any("no ids" in w for w in warnings)


def test_unknown_id_warns_and_dropped():
    diagram, warnings = parse('node a "A"\nlayer 1: a ghost')
    assert diagram.layers[0].ids == ("a",)
    assert any("unknown id 'ghost'" in w for w in warnings)


def test_duplicate_membership_first_wins():
    diagram, warnings = parse(
        'node a "A"\nnode b "B"\nlayer 1: a\nlayer 2: a b'
    )
    assert diagram.layers[0].ids == ("a",)
    assert diagram.layers[1].ids == ("b",)
    assert any("already in a layer" in w for w in warnings)


def test_group_can_be_a_layer_member():
    diagram, warnings = parse(
        'group g "G"\nnode a "A" in=g\nlayer 1: g'
    )
    assert warnings == []
    assert diagram.layers[0].ids == ("g",)


# --- Layout ---------------------------------------------------------------


def test_two_columns_side_by_side_in_index_order():
    diagram, _ = _pipeline(
        'node a "A"\nnode b "B"\nlayer 1: a\nlayer 2: b'
    )
    positioned, _w, _h = layered.layout(diagram, THEME)
    by_id = {n.id: n for n in positioned.nodes}
    assert by_id["a"].x + by_id["a"].width <= by_id["b"].x


def test_members_of_one_layer_share_column():
    diagram, _ = _pipeline(
        'node a "A"\nnode b "B"\nnode c "C"\nlayer 1: a b\nlayer 2: c'
    )
    positioned, _w, _h = layered.layout(diagram, THEME)
    by_id = {n.id: n for n in positioned.nodes}
    assert by_id["a"].x == by_id["b"].x
    assert by_id["c"].x > by_id["a"].x


def test_unassigned_goes_to_trailing_column():
    diagram, _ = _pipeline('node a "A"\nnode z "Z"\nlayer 1: a')
    positioned, _w, _h = layered.layout(diagram, THEME)
    by_id = {n.id: n for n in positioned.nodes}
    assert by_id["z"].x > by_id["a"].x


def test_group_layer_members_stay_in_frame():
    diagram, _ = _pipeline(
        'group g "G" kind=service\n'
        'node a "A" in=g\n'
        'node b "B" in=g\n'
        'layer 1: g'
    )
    positioned, _w, _h = layered.layout(diagram, THEME)
    g = positioned.groups[0]
    for m in positioned.nodes:
        assert g.x <= m.x and m.x + m.width <= g.x + g.width


def test_layered_is_deterministic():
    source = (EXAMPLES / "pipeline.fl").read_text(encoding="utf-8")
    d1, _ = _pipeline(source)
    d2, _ = _pipeline(source)
    l1, _w1, _h1 = layered.layout(d1, THEME)
    l2, _w2, _h2 = layered.layout(d2, THEME)
    assert l1 == l2


# --- Compiler engine selection -------------------------------------------


def test_no_layers_means_stack_output_unchanged():
    source = (EXAMPLES / "hello.fl").read_text(encoding="utf-8")
    expected = (GOLDEN / "hello.svg").read_text(encoding="utf-8")
    assert compile_diagram(source, THEME) == expected


def test_layered_used_when_layers_present():
    svg = compile_diagram('node a "A"\nnode b "B"\nlayer 1: a\nlayer 2: b')
    assert svg.startswith("<svg")
    assert ">A<" in svg and ">B<" in svg


# --- Golden ---------------------------------------------------------------


def test_golden_pipeline():
    source = (EXAMPLES / "pipeline.fl").read_text(encoding="utf-8")
    expected = (GOLDEN / "pipeline.svg").read_text(encoding="utf-8")
    assert compile_diagram(source, THEME) == expected
