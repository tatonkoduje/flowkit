"""FlowLite DSL parser: ``.fl`` text -> :class:`~flowlite.model.Diagram`.

The parser reads one instruction per line. Blank lines and ``#`` comments are
ignored. Unparseable lines are collected as warnings and never abort parsing.
"""

from __future__ import annotations

import re
from dataclasses import replace
from pathlib import Path

from . import icons
from .model import Diagram, Edge, Group, Layer, Node, Radial, Table

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
    )
    return diagram, warnings


def parse_file(path: Path) -> tuple[Diagram, list[str]]:
    """Read ``path`` and parse it."""
    return parse(Path(path).read_text(encoding="utf-8"))
