"""Timeline (Gantt) tests (change 0012)."""

from __future__ import annotations

import re
from datetime import date
from pathlib import Path

from flowlite.compiler import compile_diagram
from flowlite.layout import timeline as tl_layout
from flowlite.parser import parse
from flowlite.themes import load_theme

EXAMPLES = Path(__file__).resolve().parents[1] / "examples"
GOLDEN = Path(__file__).resolve().parent / "golden"
THEME = load_theme("midnight")


# --- Parser: head ---------------------------------------------------------


def test_timeline_head_title_range():
    d, w = parse(
        'timeline "T" "Sub" from 2026-05-01 to 2026-06-01'
    )
    assert w == []
    assert d.timeline is not None
    assert d.timeline.title == "T"
    assert d.timeline.subtitle == "Sub"
    assert d.timeline.start == date(2026, 5, 1)
    assert d.timeline.end == date(2026, 6, 1)


def test_default_axis_is_month():
    d, _ = parse('timeline "T"')
    assert d.timeline.axis == "month"
    assert d.timeline.grid == ""


# --- Parser: sections and bars -------------------------------------------


def test_section_with_color():
    d, w = parse('timeline "T"\nsection "Discovery" color=blue')
    assert w == []
    assert d.timeline.sections[0].title == "Discovery"
    assert d.timeline.sections[0].color == "blue"


def test_bar_start_end_and_section():
    d, w = parse(
        'timeline "T"\nsection "S" color=red\n'
        'bar "Work" 2026-05-01 -> 2026-05-10 section="S"'
    )
    assert w == []
    item = d.timeline.items[0]
    assert item.label == "Work"
    assert item.start == date(2026, 5, 1)
    assert item.end == date(2026, 5, 10)
    assert item.section == "S"


def test_bar_uses_current_section_when_omitted():
    d, _ = parse('timeline "T"\nsection "S"\nbar "W" 2026-05-01 -> 2026-05-02')
    assert d.timeline.items[0].section == "S"


def test_single_day_bar():
    d, _ = parse('timeline "T"\nbar "One" 2026-05-01 -> 2026-05-01')
    item = d.timeline.items[0]
    assert item.start == item.end


def test_state_and_note():
    d, _ = parse(
        'timeline "T"\nsection "S"\n'
        'bar "W" 2026-05-01 -> 2026-05-02 section="S" state=active note="in progress"'
    )
    item = d.timeline.items[0]
    assert item.state == "active"
    assert item.note == "in progress"


def test_milestone():
    d, w = parse('timeline "T"\nsection "S"\nmilestone "M" 2026-05-01 section="S"')
    assert w == []
    item = d.timeline.items[0]
    assert item.milestone is True
    assert item.start == item.end == date(2026, 5, 1)


# --- Parser: axis / grid / marker ----------------------------------------


def test_axis_with_grid():
    d, w = parse('timeline "T"\naxis month grid week')
    assert w == []
    assert d.timeline.axis == "month"
    assert d.timeline.grid == "week"


# --- Parser: spacing attributes (0013) ------------------------------------


def test_week_parsed():
    d, w = parse('timeline "T" week=72')
    assert w == []
    assert d.timeline.week == 72.0
    assert d.timeline.width is None


def test_width_parsed():
    d, w = parse('timeline "T" width=1600')
    assert w == []
    assert d.timeline.width == 1600
    assert d.timeline.week is None


def test_week_default_is_none():
    d, _ = parse('timeline "T"')
    assert d.timeline.week is None
    assert d.timeline.width is None


def test_week_zero_warns_and_ignored():
    d, w = parse('timeline "T" week=0')
    assert d.timeline.week is None
    assert any("week must be a positive number" in x for x in w)


def test_week_non_numeric_warns():
    d, w = parse('timeline "T" week=abc')
    assert d.timeline.week is None
    assert any("week must be a positive number" in x for x in w)


def test_width_non_numeric_warns():
    d, w = parse('timeline "T" width=wide')
    assert d.timeline.width is None
    assert any("width must be a positive number" in x for x in w)


def test_width_overrides_week():
    d, w = parse('timeline "T" week=80 width=1600')
    assert d.timeline.width == 1600
    assert d.timeline.week is None
    assert any("width overrides week" in x for x in w)


def test_marker():
    d, w = parse('timeline "T"\nmarker 2026-05-21 "Start here"')
    assert w == []
    assert d.timeline.markers[0].date == date(2026, 5, 21)
    assert d.timeline.markers[0].label == "Start here"


# --- Parser: warnings -----------------------------------------------------


def test_bar_outside_timeline_warns():
    d, w = parse('bar "W" 2026-05-01 -> 2026-05-02')
    assert d.timeline is None
    assert any("outside a timeline" in x for x in w)


def test_section_outside_timeline_warns():
    _d, w = parse('section "S"')
    assert any("outside a timeline" in x for x in w)


def test_end_before_start_swapped():
    d, _ = parse(
        'timeline "T"\nsection "S"\nbar "W" 2026-05-10 -> 2026-05-01 section="S"'
    )
    item = d.timeline.items[0]
    assert item.start < item.end


def test_unknown_state_warns():
    d, w = parse(
        'timeline "T"\nsection "S"\nbar "W" 2026-05-01 -> 2026-05-02 section="S" state=weird'
    )
    assert d.timeline.items[0].state == "normal"
    assert any("unknown state" in x for x in w)


def test_unknown_axis_warns():
    _d, w = parse('timeline "T"\naxis yearly')
    assert any("unknown axis" in x for x in w)


def test_unknown_section_warns():
    _d, w = parse(
        'timeline "T"\nsection "S"\nbar "W" 2026-05-01 -> 2026-05-02 section="ghost"'
    )
    assert any("unknown section 'ghost'" in x for x in w)


def test_timeline_wins_over_graph():
    d, w = parse('timeline "T"\nnode a "A"')
    assert d.timeline is not None
    assert any("ignored" in x for x in w)


# --- Layout ---------------------------------------------------------------


def _tl(source: str):
    d, _ = parse(source)
    return tl_layout.layout(d.timeline, THEME)


def test_range_derived_from_items():
    placed = _tl('timeline "T"\nsection "S"\nbar "W" 2026-05-01 -> 2026-05-31 section="S"')
    assert placed.width > 0 and placed.height > 0


def test_x_is_monotonic_in_date():
    placed = _tl(
        'timeline "T" from 2026-05-01 to 2026-08-01\nsection "S"\n'
        'bar "A" 2026-05-10 -> 2026-05-20 section="S"\n'
        'bar "B" 2026-06-10 -> 2026-06-20 section="S"'
    )
    a, b = placed.items
    assert a.x < b.x


def test_sections_stack_in_declaration_order():
    placed = _tl(
        'timeline "T"\nsection "One"\nsection "Two"\n'
        'bar "A" 2026-05-01 -> 2026-05-02 section="One"\n'
        'bar "B" 2026-05-03 -> 2026-05-04 section="Two"'
    )
    assert placed.sections[0].y < placed.sections[1].y


def test_single_day_bar_has_min_width():
    placed = _tl('timeline "T"\nsection "S"\nbar "One" 2026-05-01 -> 2026-05-01 section="S"')
    assert placed.items[0].w >= tl_layout.BAR_MIN_W


def test_milestone_centred_on_date():
    placed = _tl(
        'timeline "T" from 2026-05-01 to 2026-08-01\nsection "S"\n'
        'milestone "M" 2026-06-15 section="S"'
    )
    m = placed.items[0]
    # The diamond's centre x sits within the plot.
    assert placed.plot_x0 <= m.x + m.w / 2 <= placed.plot_x1


def test_layout_is_deterministic():
    src = (EXAMPLES / "timeline.fl").read_text(encoding="utf-8")
    p1 = tl_layout.layout(parse(src)[0].timeline, THEME)
    p2 = tl_layout.layout(parse(src)[0].timeline, THEME)
    assert p1 == p2


# --- Layout: spacing (0013) ----------------------------------------------


def _chart(width_attr: str) -> float:
    placed = _tl(
        f'timeline "T" from 2026-05-01 to 2026-08-01 {width_attr}'
        '\nsection "S"\nbar "W" 2026-05-10 -> 2026-05-20 section="S"'
    )
    return placed.plot_x1 - placed.plot_x0


def test_larger_week_gives_wider_chart():
    narrow = _chart("week=46")
    wide = _chart("week=92")
    assert wide > narrow


def test_week_is_proportional():
    a = _chart("week=46")
    b = _chart("week=92")
    # doubling the week spacing doubles the plot width
    assert abs(b - 2 * a) < 2


def test_width_sets_plot_width_exactly():
    placed = _tl(
        'timeline "T" from 2026-05-01 to 2026-08-01 width=1600'
        '\nsection "S"\nbar "W" 2026-05-10 -> 2026-05-20 section="S"'
    )
    assert abs((placed.plot_x1 - placed.plot_x0) - 1600) < 0.5


def test_dates_stay_within_plot_with_width():
    placed = _tl(
        'timeline "T" from 2026-05-01 to 2026-08-01 width=1200'
        '\nsection "S"\nbar "W" 2026-05-10 -> 2026-05-20 section="S"'
    )
    for item in placed.items:
        assert placed.plot_x0 <= item.x <= placed.plot_x1


def test_grid_spans_before_start():
    # A weekly grid must show a FULL week before the start marker: the domain
    # starts on the Monday of the week before the start week.
    placed = _tl(
        'timeline "T" from 2026-05-21 to 2026-06-30'
        '\naxis month grid week'
        '\nsection "S"\nbar "W" 2026-05-21 -> 2026-05-22 section="S"'
    )
    grid_dates = [t.date for t in placed.grid_ticks]
    # 2026-05-21 is a Thursday; its week's Monday is 2026-05-18, so the domain
    # starts a full week earlier: 2026-05-11.
    assert date(2026, 5, 11) in grid_dates
    assert date(2026, 5, 18) in grid_dates
    assert abs(placed.grid_ticks[0].x - placed.plot_x0) < 0.5  # at the left edge


def test_axis_ticks_bounded_by_plot():
    # No axis tick may be drawn left of the plot's left edge.
    placed = _tl(
        'timeline "T" from 2026-05-21 to 2026-06-30'
        '\naxis month grid week'
        '\nsection "S"\nbar "W" 2026-05-21 -> 2026-05-22 section="S"'
    )
    for tick in placed.axis_ticks:
        assert tick.x >= placed.plot_x0 - 0.5


def test_marker_sits_inside_plot_with_grid():
    # The start marker (range start) must be to the RIGHT of the plot's left
    # edge so a full week of gray grid precedes it.
    placed = _tl(
        'timeline "T" from 2026-05-21 to 2026-06-30'
        '\naxis month grid week'
        '\nmarker 2026-05-21 "Start"'
        '\nsection "S"\nbar "W" 2026-05-21 -> 2026-05-22 section="S"'
    )
    marker = placed.markers[0]
    assert marker.x > placed.plot_x0 + 30  # at least a week in
    # And at least two gridlines exist to its left.
    assert sum(1 for t in placed.grid_ticks if t.x < marker.x) >= 2


def test_no_grid_keeps_domain_at_range_start():
    # Without a weekly grid the range start stays at the plot's left edge.
    placed = _tl(
        'timeline "T" from 2026-05-21 to 2026-06-30'
        '\nmarker 2026-05-21 "Start"'
        '\nsection "S"\nbar "W" 2026-05-21 -> 2026-05-22 section="S"'
    )
    assert abs(placed.markers[0].x - placed.plot_x0) < 0.5


# --- Render ---------------------------------------------------------------


def test_render_has_title_sections_and_labels():
    svg = compile_diagram(
        'timeline "Big Chart"\nsection "Discovery"\n'
        'bar "Research" 2026-05-01 -> 2026-06-01 section="Discovery"'
    )
    assert "Big Chart" in svg
    assert "Discovery" in svg
    assert "Research" in svg


def test_render_escapes_text():
    svg = compile_diagram('timeline "A & B"\nsection "S <x>"')
    assert "&amp;" in svg
    assert "&lt;x&gt;" in svg


def test_marker_line_drawn():
    svg = compile_diagram('timeline "T" from 2026-05-01 to 2026-07-01\nmarker 2026-05-21 "S"')
    assert "#F5CD47" in svg  # marker colour
    assert "stroke-dasharray" in svg


def test_done_and_active_differ():
    base = (
        'timeline "T"\nsection "S" color=blue\n'
        'bar "W" 2026-05-01 -> 2026-05-02 section="S" state='
    )
    done = compile_diagram(base + "done")
    active = compile_diagram(base + "active")
    # `done` mutes the section colour, so the bar fill differs from `active`.
    pat = (r'<rect x="[\d.]+" y="[\d.]+" width="[\d.]+" height="[\d.]+" '
           r'rx="[^"]+" fill="(#[0-9A-F]{6})"')
    done_fill = re.search(pat, done)
    active_fill = re.search(pat, active)
    assert done_fill and active_fill
    assert done_fill.group(1) != active_fill.group(1)


# --- Compiler / golden ----------------------------------------------------


def test_no_timeline_leaves_graph_unchanged():
    source = (EXAMPLES / "hello.fl").read_text(encoding="utf-8")
    expected = (GOLDEN / "hello.svg").read_text(encoding="utf-8")
    assert compile_diagram(source, THEME) == expected


def test_golden_timeline():
    source = (EXAMPLES / "timeline.fl").read_text(encoding="utf-8")
    expected = (GOLDEN / "timeline.svg").read_text(encoding="utf-8")
    assert compile_diagram(source, THEME) == expected
