"""FlowLite DSL parser: ``.fl`` text -> :class:`~flowlite.model.Diagram`.

The parser reads one instruction per line. Blank lines and ``#`` comments are
ignored. Unparseable lines are collected as warnings and never abort parsing.
"""

from __future__ import annotations

import re
from dataclasses import replace
from datetime import date
from pathlib import Path

from . import icons
from .model import (
    Diagram,
    Edge,
    Group,
    Layer,
    Marker,
    Node,
    Radial,
    Table,
    Timeline,
    TimelineItem,
    TimelineSection,
)

TITLE_RE = re.compile(r'^title\s+"([^"]*)"(?:\s+"([^"]*)")?\s*$')
THEME_RE = re.compile(r"^theme\s+(\w+)\s*$")
# Attributes not understood yet are tolerated and ignored, so a richer source
# degrades gracefully instead of dropping the whole instruction.
NODE_RE = re.compile(r'^node\s+(\w+)\s+"([^"]*)"(.*)$')
NODE_KIND_RE = re.compile(r"\bkind=(\w+)")
NODE_SHAPE_RE = re.compile(r"\bshape=(\w+)")
NODE_IN_RE = re.compile(r"\bin=(\w+)")
NODE_ICON_RE = re.compile(r"\bicon=([\w-]+)")
NODE_LINK_RE = re.compile(r"\blink=(\S+)")
NODE_LINK_ANY_RE = re.compile(r"\blink=")
GROUP_RE = re.compile(r'^group\s+(\w+)\s+"([^"]*)"(.*)$')
EDGE_RE = re.compile(r"^edge\s+(\w+)\s*->\s*(\w+)(.*)$")
LAYER_RE = re.compile(r"^layer\s+(\d+)\s*:\s*(.*)$")
LAYOUT_RE = re.compile(r"^layout\s+(\w+)\s*$")
TABLE_RE = re.compile(r'^table\s+(\w+)\s+"([^"]*)"(.*)$')
COL_RE = re.compile(r"^col\s*:\s*(.*)$")
ROW_RE = re.compile(r"^row\s*:\s*(.*)$")
RADIAL_RE = re.compile(r"^radial\b(.*)$")
RADIAL_HUB_RE = re.compile(r"\bhub=(\w+)")
RADIAL_NUM_RE = re.compile(r"\b(radius|start|gap)=(-?\d+(?:\.\d+)?)\b")
RADIAL_BAD_NUM_RE = re.compile(r"\b(radius|start|gap)=(?!-?\d+(?:\.\d+)?\b)\S+")
RADIAL_DOCK_RE = re.compile(r"\bdock\b")
EDGE_LABEL_RE = re.compile(r'^\s*"([^"]*)"')
EDGE_ATTR_RE = re.compile(r"\b(style|arrow|curve)=(\w+)")

# Timeline instructions.
TIMELINE_RE = re.compile(r'^timeline\s+"([^"]*)"(?:\s+"([^"]*)")?(.*)$')
SECTION_RE = re.compile(r'^section\s+"([^"]*)"(.*)$')
BAR_RE = re.compile(
    r'^bar\s+"([^"]*)"\s+(\d{4}-\d{2}-\d{2})\s*->\s*(\d{4}-\d{2}-\d{2})(.*)$'
)
MILESTONE_RE = re.compile(r'^milestone\s+"([^"]*)"\s+(\d{4}-\d{2}-\d{2})(.*)$')
AXIS_RE = re.compile(r"^axis\s+(\w+)(?:\s+grid\s+(\w+))?$")
MARKER_RE = re.compile(r'^marker\s+(today|\d{4}-\d{2}-\d{2})(?:\s+"([^"]*)")?$')
TL_SECTION_RE = re.compile(r'\bsection="([^"]*)"')
TL_COLOR_RE = re.compile(r"\bcolor=(\w+|#[0-9A-Fa-f]{3,8})")
TL_STATE_RE = re.compile(r"\bstate=(\w+)")
TL_NOTE_RE = re.compile(r'\bnote="([^"]*)"')
TL_FROM_RE = re.compile(r"\bfrom\s+(\d{4}-\d{2}-\d{2})")
TL_TO_RE = re.compile(r"\bto\s+(\d{4}-\d{2}-\d{2})")
TL_WEEK_RE = re.compile(r"\bweek=(\d+(?:\.\d+)?)")
TL_WIDTH_RE = re.compile(r"\bwidth=(\d+)")
TL_WEEK_ANY_RE = re.compile(r"\bweek=(\S+)")
TL_WIDTH_ANY_RE = re.compile(r"\bwidth=(\S+)")

#: Allowed timeline enums.
TL_UNITS = ("day", "week", "month")
TL_STATES = ("normal", "done", "active", "planned")

#: Named shapes. ``polyN`` (N = 3..12) is handled separately.
NAMED_SHAPES = ("card", "db", "hub", "hex", "pill", "diamond")

#: Allowed edge attribute values.
EDGE_STYLES = ("normal", "dashed", "bold")
EDGE_ARROWS = ("normal", "dot", "none")
EDGE_CURVES = ("bezier", "straight")


def _is_known_shape(shape: str) -> bool:
    if shape in NAMED_SHAPES:
        return True
    return shape.startswith("poly") and shape[4:].isdigit()


def _parse_date(text: str) -> "date | None":
    """Parse an ISO ``YYYY-MM-DD`` date; ``None`` if invalid."""
    try:
        return date.fromisoformat(text)
    except ValueError:
        return None


def _timeline_item(
    label: str,
    start: "date",
    end: "date",
    rest: str,
    current_section: str,
    warnings: list[str],
    lineno: int,
    milestone: bool = False,
) -> TimelineItem:
    """Build a timeline item from a bar/milestone tail with its attributes."""
    section_match = TL_SECTION_RE.search(rest)
    section = section_match.group(1) if section_match else current_section
    color_match = TL_COLOR_RE.search(rest)
    state_match = TL_STATE_RE.search(rest)
    note_match = TL_NOTE_RE.search(rest)
    state = "normal"
    if state_match:
        if state_match.group(1) in TL_STATES:
            state = state_match.group(1)
        else:
            warnings.append(
                f"line {lineno}: unknown state '{state_match.group(1)}', "
                f"using 'normal'"
            )
    return TimelineItem(
        label=label,
        start=start,
        end=end,
        section=section,
        color=color_match.group(1) if color_match else "",
        state=state,
        note=note_match.group(1) if note_match else "",
        milestone=milestone,
    )


def parse(text: str) -> tuple[Diagram, list[str]]:
    """Parse ``text`` into a :class:`Diagram` plus a list of warnings.

    Warnings describe lines that could not be parsed; they do not stop parsing.
    """
    title, subtitle, theme = "Diagram", "", "midnight"
    nodes: list[Node] = []
    groups: list[Group] = []
    edges: list[Edge] = []
    layers: list[Layer] = []
    radial: Radial | None = None
    tables: list[Table] = []
    current_table: int | None = None
    auto_layout = False
    # Timeline state (mutually exclusive with the graph). `tl_*` are mutable
    # holders filled while parsing and frozen into a Timeline at the end.
    tl_open = False
    tl_title, tl_subtitle = "", ""
    tl_start: "date | None" = None
    tl_end: "date | None" = None
    tl_axis, tl_grid = "month", ""
    tl_week: float | None = None
    tl_width: int | None = None
    tl_sections: list[TimelineSection] = []
    tl_items: list[TimelineItem] = []
    tl_markers: list[Marker] = []
    tl_current_section = ""
    warnings: list[str] = []

    for lineno, raw in enumerate(text.splitlines(), start=1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue

        # A `col:`/`row:` line belongs to the most recent `table`; any other
        # instruction closes that table.
        m = COL_RE.match(line) if current_table is not None else None
        if m:
            cells = tuple(c.strip() for c in m.group(1).split("|"))
            table = tables[current_table]  # type: ignore[index]
            if table.header:
                warnings.append(
                    f"line {lineno}: table '{table.id}' already has a header, ignored"
                )
            else:
                tables[current_table] = replace(table, header=cells)  # type: ignore[index]
            continue

        m = ROW_RE.match(line) if current_table is not None else None
        if m:
            cells = tuple(c.strip() for c in m.group(1).split("|"))
            table = tables[current_table]  # type: ignore[index]
            width = table.columns
            if width and len(cells) > width:
                warnings.append(
                    f"line {lineno}: table '{table.id}' row has {len(cells)} "
                    f"cells, keeping {width}"
                )
                cells = cells[:width]
            tables[current_table] = replace(  # type: ignore[index]
                table, rows=(*table.rows, cells)
            )
            continue

        # Any other instruction ends the current table.
        current_table = None

        m = COL_RE.match(line)
        if m or ROW_RE.match(line):
            warnings.append(f"line {lineno}: '{line.split(':', 1)[0]}:' without a table")
            continue

        m = TITLE_RE.match(line)
        if m:
            title = m.group(1)
            subtitle = m.group(2) or ""
            continue

        m = THEME_RE.match(line)
        if m:
            theme = m.group(1)
            continue

        m = TABLE_RE.match(line)
        if m:
            kind_match = NODE_KIND_RE.search(m.group(3))
            kind = kind_match.group(1) if kind_match else "default"
            ids = {t.id for t in tables}
            if m.group(1) in ids:
                warnings.append(
                    f"line {lineno}: table '{m.group(1)}' already declared, ignored"
                )
            else:
                tables.append(Table(id=m.group(1), title=m.group(2), kind=kind))
                current_table = len(tables) - 1
            continue

        m = NODE_RE.match(line)
        if m:
            rest = m.group(3)
            kind_match = NODE_KIND_RE.search(rest)
            kind = kind_match.group(1) if kind_match else "default"
            shape_match = NODE_SHAPE_RE.search(rest)
            shape = "card"
            if shape_match:
                shape = shape_match.group(1)
                if not _is_known_shape(shape):
                    warnings.append(
                        f"line {lineno}: unknown shape '{shape}', using 'card'"
                    )
                    shape = "card"
            in_match = NODE_IN_RE.search(rest)
            group_id = in_match.group(1) if in_match else ""
            icon_match = NODE_ICON_RE.search(rest)
            icon = ""
            if icon_match:
                icon = icon_match.group(1)
                if icons.icon_path(icon) is None:
                    warnings.append(
                        f"line {lineno}: unknown icon '{icon}', ignored"
                    )
                    icon = ""
            link_match = NODE_LINK_RE.search(rest)
            if link_match:
                link = link_match.group(1)
            elif NODE_LINK_ANY_RE.search(rest):
                warnings.append(f"line {lineno}: empty link, ignored")
                link = ""
            else:
                link = ""
            nodes.append(
                Node(
                    id=m.group(1),
                    label=m.group(2),
                    kind=kind,
                    shape=shape,
                    group=group_id,
                    icon=icon,
                    link=link,
                )
            )
            continue

        m = GROUP_RE.match(line)
        if m:
            kind_match = NODE_KIND_RE.search(m.group(3))
            kind = kind_match.group(1) if kind_match else "default"
            groups.append(Group(id=m.group(1), title=m.group(2), kind=kind))
            continue

        m = LAYER_RE.match(line)
        if m:
            ids = tuple(m.group(2).split())
            if not ids:
                warnings.append(f"line {lineno}: layer {m.group(1)} has no ids")
            else:
                layers.append(Layer(index=int(m.group(1)), ids=ids))
            continue

        m = LAYOUT_RE.match(line)
        if m:
            if m.group(1) == "auto":
                auto_layout = True
            else:
                warnings.append(
                    f"line {lineno}: unknown layout '{m.group(1)}', "
                    f"expected 'auto'"
                )
            continue

        m = RADIAL_RE.match(line)
        if m:
            rest = m.group(1)
            hub_match = RADIAL_HUB_RE.search(rest)
            if hub_match is None:
                warnings.append(f"line {lineno}: radial requires hub=<id>")
            elif radial is not None:
                warnings.append(f"line {lineno}: radial already declared, ignored")
            else:
                attrs: dict[str, float] = {}
                for key, value in RADIAL_NUM_RE.findall(rest):
                    attrs[key] = float(value)
                # Warn on a numeric attribute given a non-numeric value.
                for bad in RADIAL_BAD_NUM_RE.findall(rest):
                    warnings.append(
                        f"line {lineno}: radial {bad} is not a number, ignored"
                    )
                radial = Radial(
                    hub=hub_match.group(1),
                    radius=attrs.get("radius"),
                    start=attrs.get("start", -90.0),
                    dock=bool(RADIAL_DOCK_RE.search(rest)),
                    gap=attrs.get("gap", 70.0),
                )
            continue

        m = TIMELINE_RE.match(line)
        if m:
            tl_open = True
            tl_title, tl_subtitle = m.group(1), m.group(2) or ""
            rest = m.group(3)
            from_match, to_match = TL_FROM_RE.search(rest), TL_TO_RE.search(rest)
            if from_match:
                tl_start = _parse_date(from_match.group(1))
            if to_match:
                tl_end = _parse_date(to_match.group(1))
            week_match = TL_WEEK_RE.search(rest)
            width_match = TL_WIDTH_RE.search(rest)
            if week_match:
                value = float(week_match.group(1))
                if value > 0:
                    tl_week = value
                else:
                    warnings.append(
                        f"line {lineno}: week must be a positive number, ignored"
                    )
            elif TL_WEEK_ANY_RE.search(rest):
                warnings.append(
                    f"line {lineno}: week must be a positive number, ignored"
                )
            if width_match:
                value_w = int(width_match.group(1))
                if value_w > 0:
                    tl_width = value_w
                else:
                    warnings.append(
                        f"line {lineno}: width must be a positive number, ignored"
                    )
            elif TL_WIDTH_ANY_RE.search(rest):
                warnings.append(
                    f"line {lineno}: width must be a positive number, ignored"
                )
            if tl_width is not None and tl_week is not None:
                warnings.append(
                    f"line {lineno}: width overrides week, ignoring week"
                )
                tl_week = None
            continue

        if tl_open:
            m = SECTION_RE.match(line)
            if m:
                color_match = TL_COLOR_RE.search(m.group(2))
                tl_sections.append(
                    TimelineSection(
                        title=m.group(1),
                        color=color_match.group(1) if color_match else "",
                    )
                )
                tl_current_section = m.group(1)
                continue

            m = BAR_RE.match(line)
            if m:
                start, end = _parse_date(m.group(2)), _parse_date(m.group(3))
                assert start is not None and end is not None  # regex guarantees
                if end < start:
                    warnings.append(
                        f"line {lineno}: bar '{m.group(1)}' end before start, swapped"
                    )
                    start, end = end, start
                rest = m.group(4)
                tl_items.append(
                    _timeline_item(
                        m.group(1), start, end, rest, tl_current_section, warnings, lineno
                    )
                )
                continue

            m = MILESTONE_RE.match(line)
            if m:
                when = _parse_date(m.group(2))
                assert when is not None
                tl_items.append(
                    _timeline_item(
                        m.group(1), when, when, m.group(3), tl_current_section,
                        warnings, lineno, milestone=True,
                    )
                )
                continue

            m = AXIS_RE.match(line)
            if m:
                if m.group(1) in TL_UNITS:
                    tl_axis = m.group(1)
                else:
                    warnings.append(
                        f"line {lineno}: unknown axis '{m.group(1)}', using 'month'"
                    )
                if m.group(2):
                    if m.group(2) in TL_UNITS:
                        tl_grid = m.group(2)
                    else:
                        warnings.append(
                            f"line {lineno}: unknown grid '{m.group(2)}', ignored"
                        )
                continue

            m = MARKER_RE.match(line)
            if m:
                when = _parse_date(m.group(1)) if m.group(1) != "today" else None
                if when is None:
                    warnings.append(
                        f"line {lineno}: marker 'today' needs an explicit date, ignored"
                    )
                else:
                    tl_markers.append(Marker(date=when, label=m.group(2) or ""))
                continue

        m = EDGE_RE.match(line)
        if m:
            rest = m.group(3)
            label = ""
            label_match = EDGE_LABEL_RE.match(rest)
            if label_match:
                label = label_match.group(1)
            attrs = {"style": "normal", "arrow": "normal", "curve": "bezier"}
            allowed = {
                "style": EDGE_STYLES,
                "arrow": EDGE_ARROWS,
                "curve": EDGE_CURVES,
            }
            for key, value in EDGE_ATTR_RE.findall(rest):
                if value in allowed[key]:
                    attrs[key] = value
                else:
                    warnings.append(
                        f"line {lineno}: unknown {key} '{value}', "
                        f"using '{attrs[key]}'"
                    )
            edges.append(
                Edge(
                    src=m.group(1),
                    dst=m.group(2),
                    label=label,
                    style=attrs["style"],
                    arrow=attrs["arrow"],
                    curve=attrs["curve"],
                )
            )
            continue

        # Timeline instructions given before any `timeline` header.
        if (
            SECTION_RE.match(line)
            or BAR_RE.match(line)
            or MILESTONE_RE.match(line)
            or AXIS_RE.match(line)
            or MARKER_RE.match(line)
        ):
            warnings.append(f"line {lineno}: timeline instruction outside a timeline")
            continue

        warnings.append(f"line {lineno}: cannot parse: {line}")

    # Detach nodes that reference an unknown group.
    known_groups = {g.id for g in groups}
    for i, node in enumerate(nodes):
        if node.group and node.group not in known_groups:
            warnings.append(
                f"node {node.id} references unknown group '{node.group}'"
            )
            nodes[i] = replace(node, group="")

    # Validate layer membership: known ids only, first assignment wins.
    known_items = {n.id for n in nodes} | known_groups | {t.id for t in tables}
    seen: set[str] = set()
    clean_layers: list[Layer] = []
    for layer in layers:
        kept: list[str] = []
        for item_id in layer.ids:
            if item_id not in known_items:
                warnings.append(
                    f"layer {layer.index}: unknown id '{item_id}', ignored"
                )
            elif item_id in seen:
                warnings.append(
                    f"layer {layer.index}: '{item_id}' already in a layer, ignored"
                )
            else:
                seen.add(item_id)
                kept.append(item_id)
        clean_layers.append(Layer(index=layer.index, ids=tuple(kept)))

    # Validate radial hub references a known node.
    if radial is not None and radial.hub not in {n.id for n in nodes}:
        warnings.append(f"radial hub '{radial.hub}' is not a node, ignored")
        radial = None
    elif radial is not None and radial.dock:
        hub_node = next(n for n in nodes if n.id == radial.hub)
        if hub_node.shape != "hex" and hub_node.shape != "diamond" and not (
            hub_node.shape.startswith("poly")
        ):
            warnings.append(
                f"radial dock needs a polygon hub, "
                f"'{hub_node.shape}' ignores it"
            )
            radial = replace(radial, dock=False)

    # `layout auto` yields to an explicit layer/radial override.
    if auto_layout and clean_layers:
        warnings.append("layout auto ignored: explicit 'layer' columns are used")
        auto_layout = False
    if auto_layout and radial is not None:
        warnings.append("layout auto ignored: 'radial' is used")
        auto_layout = False

    # Build the timeline, if an instruction opened one. A timeline wins over any
    # graph instructions in the same source.
    timeline: Timeline | None = None
    if tl_open:
        if nodes or edges or groups or tables:
            warnings.append("timeline present: node/edge/group/table ignored")
        known_sections = {s.title for s in tl_sections}
        for item in tl_items:
            if item.section and item.section not in known_sections:
                warnings.append(
                    f"timeline item '{item.label}' references unknown "
                    f"section '{item.section}'"
                )
        timeline = Timeline(
            title=tl_title,
            subtitle=tl_subtitle,
            start=tl_start,
            end=tl_end,
            axis=tl_axis,
            grid=tl_grid,
            sections=tuple(tl_sections),
            items=tuple(tl_items),
            markers=tuple(tl_markers),
            week=tl_week,
            width=tl_width,
        )

    diagram = Diagram(
        title=title,
        subtitle=subtitle,
        theme=theme,
        nodes=tuple(nodes),
        groups=tuple(groups),
        edges=tuple(edges),
        layers=tuple(clean_layers),
        radial=radial,
        tables=tuple(tables),
        auto_layout=auto_layout,
        timeline=timeline,
    )
    return diagram, warnings


def parse_file(path: Path) -> tuple[Diagram, list[str]]:
    """Read ``path`` and parse it."""
    return parse(Path(path).read_text(encoding="utf-8"))
