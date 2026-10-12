"""Auto-layout tests (change 0011)."""

from __future__ import annotations

from dataclasses import replace
from pathlib import Path

from flowlite.compiler import compile_diagram
from flowlite.layout import auto, layered
from flowlite.measure import measure
from flowlite.parser import parse
from flowlite.themes import load_theme

EXAMPLES = Path(__file__).resolve().parents[1] / "examples"
GOLDEN = Path(__file__).resolve().parent / "golden"
THEME = load_theme("midnight")


def _measured(source: str):
    diagram, warnings = parse(source)
    return measure(diagram, THEME), warnings


def _layers(source: str) -> list[tuple[str, ...]]:
    measured, _ = _measured(source)
    derived = auto.derive_layers(measured)
    return [layer.ids for layer in derived]


# --- Parser ---------------------------------------------------------------


def test_layout_auto_sets_flag():
    diagram, warnings = parse('node a "A"\nlayout auto')
    assert warnings == []
    assert diagram.auto_layout is True


def test_default_is_not_auto():
    diagram, warnings = parse('node a "A"')
    assert warnings == []
    assert diagram.auto_layout is False


def test_unknown_layout_warns():
    diagram, warnings = parse('node a "A"\nlayout spiral')
    assert diagram.auto_layout is False
    assert any("unknown layout 'spiral'" in w for w in warnings)


def test_layout_auto_yields_to_explicit_layer():
    diagram, warnings = parse(
        'node a "A"\nnode b "B"\nlayer 1: a\nlayer 2: b\nlayout auto'
    )
    assert diagram.auto_layout is False
    assert any("layout auto ignored" in w for w in warnings)


def test_layout_auto_yields_to_radial():
    diagram, warnings = parse(
        'node a "A" shape=hub\nnode b "B"\nradial hub=a\nlayout auto'
    )
    assert diagram.auto_layout is False
    assert any("layout auto ignored" in w for w in warnings)


# --- Layering -------------------------------------------------------------


def test_chain_gives_three_layers():
    assert _layers('node a "A"\nnode b "B"\nnode c "C"\nedge a -> b\nedge b -> c') == [
        ("a",),
        ("b",),
        ("c",),
    ]


def test_fan_out_then_in():
    # a -> b, a -> c, b -> d, c -> d
    layers = _layers(
        'node a "A"\nnode b "B"\nnode c "C"\nnode d "D"\n'
        "edge a -> b\nedge a -> c\nedge b -> d\nedge c -> d"
    )
    assert layers[0] == ("a",)
    assert set(layers[-1]) == {"d"}
    assert set(layers[1]) == {"b", "c"}


def test_cycle_is_safe_and_drops_back_edge():
    # a -> b -> a: must terminate and place a before b.
    layers = _layers('node a "A"\nnode b "B"\nedge a -> b\nedge b -> a')
    flat = [it for col in layers for it in col]
    assert sorted(flat) == ["a", "b"]  # nothing dropped
    assert flat.index("a") < flat.index("b")


def test_disconnected_node_trails():
    layers = _layers('node a "A"\nnode b "B"\nnode z "Z"\nedge a -> b')
    assert "z" in layers[-1]
    assert layers[-1] != layers[0]


def test_layering_is_deterministic():
    source = (EXAMPLES / "auto.fl").read_text(encoding="utf-8")
    d1, _ = _measured(source)
    d2, _ = _measured(source)
    assert auto.derive_layers(d1) == auto.derive_layers(d2)


# --- Layout integration ---------------------------------------------------


def test_derived_columns_flow_left_to_right():
    source = (EXAMPLES / "auto.fl").read_text(encoding="utf-8")
    diagram, _ = _measured(source)
    derived = auto.derive_layers(diagram)
    positioned, _w, _h = layered.layout(replace(diagram, layers=derived), THEME)
    by_id = {n.id: n for n in positioned.nodes}
    # web -> gw -> slip: strictly increasing x.
    assert by_id["web"].x < by_id["gw"].x < by_id["slip"].x


def test_auto_used_when_declared():
    svg = compile_diagram('node a "A"\nnode b "B"\nedge a -> b\nlayout auto')
    assert svg.startswith("<svg")
    assert ">A<" in svg and ">B<" in svg


def test_no_auto_leaves_hello_unchanged():
    source = (EXAMPLES / "hello.fl").read_text(encoding="utf-8")
    expected = (GOLDEN / "hello.svg").read_text(encoding="utf-8")
    assert compile_diagram(source, THEME) == expected


# --- Golden ---------------------------------------------------------------


def test_golden_auto():
    source = (EXAMPLES / "auto.fl").read_text(encoding="utf-8")
    expected = (GOLDEN / "auto.svg").read_text(encoding="utf-8")
    assert compile_diagram(source, THEME) == expected
