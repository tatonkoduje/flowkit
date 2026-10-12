"""Icon tests (change 0008)."""

from __future__ import annotations

from flowlite import icons
from flowlite.compiler import compile_diagram
from flowlite.parser import parse
from flowlite.themes import load_theme

THEME = load_theme("midnight")


# --- Loader ---------------------------------------------------------------


def test_icon_set_is_non_empty():
    assert len(icons.all_icons()) >= 15


def test_known_icon_has_path():
    assert icons.icon_path("database") is not None


def test_unknown_icon_is_none():
    assert icons.icon_path("definitely-not-an-icon") is None


def test_all_icon_values_are_nonempty_strings():
    for name, path in icons.all_icons().items():
        assert name and isinstance(path, str) and path.strip()


# --- Parser ---------------------------------------------------------------


def test_icon_parsed():
    diagram, warnings = parse('node a "A" icon=database')
    assert warnings == []
    assert diagram.nodes[0].icon == "database"


def test_absent_icon_is_empty():
    diagram, warnings = parse('node a "A"')
    assert warnings == []
    assert diagram.nodes[0].icon == ""


def test_unknown_icon_warns_and_clears():
    diagram, warnings = parse('node a "A" icon=ghost')
    assert diagram.nodes[0].icon == ""
    assert any("unknown icon 'ghost'" in w for w in warnings)


def test_icon_with_hyphen_parsed():
    diagram, warnings = parse('node a "A" icon=git-branch')
    assert warnings == []
    assert diagram.nodes[0].icon == "git-branch"


# --- Render ---------------------------------------------------------------


def test_icon_emits_path():
    svg = compile_diagram('node a "A" icon=database')
    assert icons.icon_path("database") in svg
    assert "translate(" in svg


def test_no_icon_emits_no_icon_path():
    svg = compile_diagram('node a "A"')
    assert icons.icon_path("database") not in svg


def test_icon_is_tinted_white():
    svg = compile_diagram('node a "A" icon=database')
    assert 'stroke="#FFFFFF"' in svg


def test_centered_shape_icon_present():
    # hub/poly place the icon above the label; still a translation group.
    svg = compile_diagram('node a "A" shape=hub icon=zap')
    assert icons.icon_path("zap") in svg


# --- Determinism ----------------------------------------------------------


def test_icons_are_deterministic():
    source = 'node a "A" icon=database\nnode b "B" icon=globe\nedge a -> b'
    assert compile_diagram(source, THEME) == compile_diagram(source, THEME)
