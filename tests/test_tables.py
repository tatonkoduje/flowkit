"""Table node tests (change 0007)."""

from __future__ import annotations

from pathlib import Path

from flowlite.compiler import compile_diagram
from flowlite.layout import layered, radial, stack
from flowlite.measure import measure, measure_table
from flowlite.model import Table
from flowlite.parser import parse
from flowlite.themes import load_theme

EXAMPLES = Path(__file__).resolve().parents[1] / "examples"
GOLDEN = Path(__file__).resolve().parent / "golden"
THEME = load_theme("midnight")


def _measured(source: str):
    diagram, warnings = parse(source)
    return measure(diagram, THEME), warnings


# --- Parser ---------------------------------------------------------------


def test_table_with_header_and_rows():
    diagram, warnings = parse(
        'table t "T"\ncol: a | b\nrow: 1 | 2\nrow: 3 | 4'
    )
    assert warnings == []
    assert len(diagram.tables) == 1
    t = diagram.tables[0]
    assert t.id == "t"
    assert t.title == "T"
    assert t.header == ("a", "b")
    assert t.rows == (("1", "2"), ("3", "4"))


def test_cells_are_trimmed():
    diagram, _ = parse('table t "T"\ncol:  a  |  b \nrow:  x  |  y ')
    t = diagram.tables[0]
    assert t.header == ("a", "b")
    assert t.rows == (("x", "y"),)


def test_table_kind_parsed():
    diagram, _ = parse('table t "T" kind=store\ncol: a')
    assert diagram.tables[0].kind == "store"


def test_col_without_table_warns():
    diagram, warnings = parse("col: a | b")
    assert diagram.tables == ()
    assert any("without a table" in w for w in warnings)


def test_row_without_table_warns():
    _diagram, warnings = parse("row: a | b")
    assert any("without a table" in w for w in warnings)


def test_duplicate_header_warns():
    diagram, warnings = parse('table t "T"\ncol: a\ncol: b')
    assert diagram.tables[0].header == ("a",)
    assert any("already has a header" in w for w in warnings)


def test_overlong_row_warns_and_truncates():
    diagram, warnings = parse('table t "T"\ncol: a | b\nrow: 1 | 2 | 3')
    assert diagram.tables[0].rows == (("1", "2"),)
    assert any("keeping 2" in w for w in warnings)


def test_short_row_allowed():
    diagram, warnings = parse('table t "T"\ncol: a | b | c\nrow: 1 | 2')
    assert warnings == []
    assert diagram.tables[0].rows == (("1", "2"),)


def test_table_closes_on_next_instruction():
    diagram, warnings = parse(
        'table t "T"\ncol: a\nrow: 1\nnode n "N"\nrow: stray'
    )
    # The stray row after `node` is not part of the table.
    assert diagram.tables[0].rows == (("1",),)
    assert any("without a table" in w for w in warnings)


def test_table_has_no_rows():
    diagram, warnings = parse('table t "T"\ncol: a | b')
    assert diagram.tables[0].rows == ()
    assert warnings == []


def test_duplicate_table_id_ignored():
    diagram, warnings = parse(
        'table t "First"\ncol: a\ntable t "Second"\ncol: b'
    )
    assert len(diagram.tables) == 1
    assert diagram.tables[0].title == "First"
    assert any("already declared" in w for w in warnings)


# --- Measure --------------------------------------------------------------


def test_measure_width_grows_with_cells():
    small, _ = parse('table t "T"\ncol: a')
    big, _ = parse('table t "T"\ncol: averyveryverylongcolumnname')
    t_small = measure_table(small.tables[0], THEME)
    t_big = measure_table(big.tables[0], THEME)
    assert t_big.width > t_small.width


def test_measure_height_formula():
    diagram, _ = parse('table t "T"\ncol: a\nrow: 1\nrow: 2')
    t = measure_table(diagram.tables[0], THEME)
    from flowlite.measure import TABLE_HEADER_H, TABLE_ROW_H, TABLE_TITLE_BAR

    assert t.height == TABLE_TITLE_BAR + TABLE_HEADER_H + 2 * TABLE_ROW_H


def test_measure_headerless_height():
    diagram, _ = parse('table t "T"\nrow: 1')
    t = measure_table(diagram.tables[0], THEME)
    from flowlite.measure import TABLE_ROW_H, TABLE_TITLE_BAR

    assert t.height == TABLE_TITLE_BAR + TABLE_ROW_H


def test_columns_from_header_or_widest_row():
    assert Table(id="t", title="T", header=("a", "b")).columns == 2
    assert Table(id="t", title="T", rows=(("a", "b", "c"),)).columns == 3


# --- Layout ---------------------------------------------------------------


def test_table_is_stacked_after_groups():
    diagram, _ = _measured('node n "N"\ntable t "T"\ncol: a\nrow: 1')
    positioned, _w, _h = stack.layout(diagram, THEME)
    assert len(positioned.tables) == 1
    t = positioned.tables[0]
    assert t.width > 0 and t.height > 0
    assert t.y > 0


def test_table_in_layer_column():
    diagram, _ = _measured(
        'node n "N"\ntable t "T"\ncol: a\nrow: 1\nlayer 1: n\nlayer 2: t'
    )
    positioned, _w, _h = layered.layout(diagram, THEME)
    t = positioned.tables[0]
    node = next(x for x in positioned.nodes if x.id == "n")
    assert t.x > node.x


def test_table_on_radial_ring():
    diagram, _ = _measured(
        'table t "T"\ncol: a\nrow: 1\nradial hub=hub\nnode hub "HUB" shape=hub'
    )
    positioned, _w, _h = radial.layout(diagram, THEME)
    assert len(positioned.tables) == 1


# --- Render ---------------------------------------------------------------


def test_table_render_contains_title_and_cells():
    svg = compile_diagram('table t "Users"\ncol: id | name\nrow: 1 | Ada')
    assert "USERS" in svg
    assert ">id<" in svg and ">name<" in svg
    assert ">Ada<" in svg


def test_table_cells_are_escaped():
    svg = compile_diagram('table t "T"\ncol: a\nrow: <b> | x')
    # The raw angle-bracket cell is escaped; no stray tag is emitted.
    assert "&lt;b&gt;" in svg


def test_edge_targets_a_table():
    svg = compile_diagram(
        'node a "A"\ntable t "TBL"\ncol: c\nrow: v\nedge a -> t'
    )
    assert svg.startswith("<svg")
    assert "TBL" in svg
    # Exactly one edge path is drawn (the edge to the table).
    assert svg.count('marker-end="url(#arrow)"') == 1


# --- Compiler engine selection -------------------------------------------


def test_no_tables_leaves_hello_unchanged():
    source = (EXAMPLES / "hello.fl").read_text(encoding="utf-8")
    expected = (GOLDEN / "hello.svg").read_text(encoding="utf-8")
    assert compile_diagram(source, THEME) == expected


def test_no_tables_leaves_pipeline_unchanged():
    source = (EXAMPLES / "pipeline.fl").read_text(encoding="utf-8")
    expected = (GOLDEN / "pipeline.svg").read_text(encoding="utf-8")
    assert compile_diagram(source, THEME) == expected


def test_tables_are_deterministic():
    source = (EXAMPLES / "schema.fl").read_text(encoding="utf-8")
    assert compile_diagram(source, THEME) == compile_diagram(source, THEME)


# --- Golden ---------------------------------------------------------------


def test_golden_schema():
    source = (EXAMPLES / "schema.fl").read_text(encoding="utf-8")
    expected = (GOLDEN / "schema.svg").read_text(encoding="utf-8")
    assert compile_diagram(source, THEME) == expected
