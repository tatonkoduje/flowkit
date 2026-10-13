"""Timeline layout: dates -> x, sections/items -> rows.

Pure geometry for the Gantt renderer. Given a :class:`~flowlite.model.Timeline`
and a theme it resolves the visible range, maps dates to x coordinates and stacks
sections and their items into rows, returning everything the renderer needs to
draw. No randomness, no ``now()`` — the range and every tick are fixed arithmetic
so the output is deterministic.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta

from ..model import Timeline, TimelineItem
from ..themes import Theme

# --- Geometry constants (px) ------------------------------------------------
GUTTER = 190.0  # left column holding section titles
TITLE_BLOCK = 120.0  # top title/subtitle area
AXIS_BLOCK = 54.0  # bottom axis labels
SECTION_PAD_TOP = 14.0
SECTION_PAD_BOTTOM = 14.0
ROW_H = 30.0
ROW_GAP = 8.0
BAR_MIN_W = 6.0  # a single-day bar still gets a visible width
WEEK_PX = 46.0  # target pixels per week (drives the plot width)
MARGIN = 70.0  # right margin after the plot


@dataclass(frozen=True)
class PlacedItem:
    item: TimelineItem
    x: float
    y: float
    w: float
    h: float
    section_index: int


@dataclass(frozen=True)
class PlacedSection:
    index: int
    title: str
    y: float
    height: float


@dataclass(frozen=True)
class Tick:
    date: date
    x: float
    label: str


@dataclass(frozen=True)
class PlacedMarker:
    date: date
    label: str
    x: float


@dataclass(frozen=True)
class TimelineLayout:
    width: int
    height: int
    plot_x0: float
    plot_x1: float
    plot_y0: float
    plot_y1: float
    sections: tuple[PlacedSection, ...]
    items: tuple[PlacedItem, ...]
    axis_ticks: tuple[Tick, ...]
    grid_ticks: tuple[Tick, ...]
    markers: tuple[PlacedMarker, ...]


_MON = [
    "Jan", "Feb", "Mar", "Apr", "May", "Jun",
    "Jul", "Aug", "Sep", "Oct", "Nov", "Dec",
]


def _resolve_range(tl: Timeline) -> tuple[date, date]:
    """Visible range: explicit from/to, else derived from items + markers."""
    dates: list[date] = []
    for item in tl.items:
        dates.extend((item.start, item.end))
    dates.extend(m.date for m in tl.markers)
    if not dates:
        base = tl.start or date(2026, 1, 1)
        return base, base + timedelta(days=30)

    lo = tl.start or min(dates)
    hi = tl.end or max(dates)
    if tl.end is None:
        hi = hi + timedelta(days=7)  # pad by one grid unit when derived
    if hi <= lo:
        hi = lo + timedelta(days=1)
    return lo, hi


def _first_monday(d: date) -> date:
    return d + timedelta(days=(7 - d.weekday()) % 7)


def _month_starts(lo: date, hi: date) -> list[date]:
    """Month-boundary ticks in ``[lo, hi]`` — the first is on/after ``lo``."""
    cur = date(lo.year, lo.month, 1)
    if cur < lo:  # lo is mid-month: start at the next month's first
        cur = date(cur.year + (cur.month // 12), (cur.month % 12) + 1, 1)
    months: list[date] = []
    while cur <= hi:
        months.append(cur)
        cur = date(cur.year + (cur.month // 12), (cur.month % 12) + 1, 1)
    return months


def layout(timeline: Timeline, theme: Theme) -> TimelineLayout:
    """Compute pixel geometry for ``timeline``."""
    lo, hi = _resolve_range(timeline)
    # With a weekly grid, extend the x-domain back a FULL week before the range
    # start (the Monday of the previous week), so a complete empty week of gray
    # grid sits before the start marker instead of a three-day sliver.
    if timeline.grid == "week":
        dom_lo = lo - timedelta(days=lo.weekday() + 7)
    else:
        dom_lo = lo
    total_days = (hi - dom_lo).days or 1

    if timeline.width is not None:
        plot_width = float(timeline.width)
    else:
        week_px = timeline.week if timeline.week is not None else WEEK_PX
        plot_width = max(240.0, total_days / 7.0 * week_px)
    plot_x0 = GUTTER
    plot_x1 = GUTTER + plot_width
    plot_y0 = TITLE_BLOCK
    plot_y1 = plot_y0 + _plot_height(timeline)

    def x_of(d: date) -> float:
        return plot_x0 + (d - dom_lo).days / total_days * plot_width

    # Section bands.
    sections: list[PlacedSection] = []
    y = plot_y0
    for i, section in enumerate(timeline.sections):
        items = _items_in(timeline.items, section.title)
        h = SECTION_PAD_TOP + SECTION_PAD_BOTTOM + max(1, len(items)) * ROW_H
        sections.append(PlacedSection(index=i, title=section.title, y=y, height=h))
        y += h

    # Items, placed in their section band.
    items: list[PlacedItem] = []
    by_section: dict[int, int] = {}
    for section in sections:
        by_section[section.index] = 0
    for item in timeline.items:
        idx = _section_index(timeline, item.section)
        if idx is None:
            continue
        section = sections[idx]
        row = by_section[idx]
        by_section[idx] = row + 1
        row_y = section.y + SECTION_PAD_TOP + row * ROW_H
        x0 = x_of(item.start)
        x1 = x_of(item.end)
        if item.milestone:
            w = ROW_H * 0.6
            x = x0 - w / 2
            items.append(PlacedItem(item, x, row_y + 4, w, w, idx))
        else:
            w = max(BAR_MIN_W, x1 - x0)
            single_day = item.end == item.start
            h = ROW_H * 0.5 if single_day else ROW_H * 0.7
            items.append(PlacedItem(item, x0, row_y + (ROW_H - h) / 2, w, h, idx))

    axis_ticks = _ticks(timeline.axis, dom_lo, hi, x_of)
    grid_ticks = (
        _ticks(timeline.grid, dom_lo, hi, x_of, week_before=False)
        if timeline.grid
        else ()
    )

    markers = tuple(
        PlacedMarker(date=m.date, label=m.label, x=x_of(m.date))
        for m in timeline.markers
    )

    width = int(plot_x1 + MARGIN)
    height = int(plot_y1 + AXIS_BLOCK)
    return TimelineLayout(
        width=width,
        height=height,
        plot_x0=plot_x0,
        plot_x1=plot_x1,
        plot_y0=plot_y0,
        plot_y1=plot_y1,
        sections=tuple(sections),
        items=tuple(items),
        axis_ticks=axis_ticks,
        grid_ticks=grid_ticks,
        markers=markers,
    )


def _plot_height(tl: Timeline) -> float:
    total = 0.0
    for section in tl.sections:
        n = len(_items_in(tl.items, section.title))
        total += SECTION_PAD_TOP + SECTION_PAD_BOTTOM + max(1, n) * ROW_H
    return total or 80.0


def _items_in(items: tuple[TimelineItem, ...], section: str) -> list[TimelineItem]:
    return [it for it in items if it.section == section]


def _section_index(tl: Timeline, title: str) -> int | None:
    for i, section in enumerate(tl.sections):
        if section.title == title:
            return i
    return None


def _ticks(unit: str, lo: date, hi: date, x_of, week_before: bool = False) -> tuple[Tick, ...]:
    """Tick dates + x for the axis/grid at ``unit`` (day/week/month).

    ``week_before`` (grid only) starts the weekly ticks on the Monday *on or
    before* ``lo`` so the leading part-week is gridded too; default starts on the
    Monday on or after ``lo``.
    """
    if unit == "month":
        dates = _month_starts(lo, hi)
        label = lambda d: f"{_MON[d.month - 1]} {d.year}"  # noqa: E731
    elif unit == "week":
        if week_before:
            first = lo - timedelta(days=lo.weekday())  # Monday of lo's week
        else:
            first = _first_monday(lo)
        dates, day = [], first
        while day <= hi:
            dates.append(day)
            day += timedelta(days=7)
        label = lambda d: f"{_MON[d.month - 1]} {d.day:02d}"  # noqa: E731
    elif unit == "day":
        dates, day = [], lo
        while day <= hi:
            dates.append(day)
            day += timedelta(days=1)
        label = lambda d: f"{d.day:02d} {_MON[d.month - 1]}"  # noqa: E731
    else:
        return ()
    return tuple(Tick(date=d, x=x_of(d), label=label(d)) for d in dates)
