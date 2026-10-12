"""Node measurement.

Sizes a node from its label and shape using the theme's design tokens (a
character-width estimate). Deterministic and dependency-free — no real font
metrics.
"""

from __future__ import annotations

import math
from dataclasses import replace

from .model import Diagram, Group, Node, Table
from .themes import Theme

MIN_WIDTH = 150.0
# Group frame metrics.
GROUP_PAD = 18.0
GROUP_TITLE_BAR = 40.0
GROUP_ROW_GAP = 14.0
GROUP_MEMBER_GAP = 18.0
# Table metrics.
TABLE_CELL_PAD_X = 14.0
TABLE_TITLE_BAR = 46.0  # title bar at the top of the table
TABLE_HEADER_H = 34.0  # the `col:` header row (present only if declared)
TABLE_ROW_H = 28.0
TABLE_MIN_COL_W = 64.0
TABLE_MIN_WIDTH = 180.0


def poly_sides(shape: str) -> int:
    """Sides for a ``polyN`` shape, clamped to 3..12 (default 6)."""
    try:
        return max(3, min(12, int(shape[4:])))
    except (ValueError, IndexError):
        return 6


def measure_node(node: Node, theme: Theme) -> Node:
    """Return a copy of ``node`` with width/height filled in."""
    lines = node.label.split("|")
    text_w = max((len(line) for line in lines), default=0) * theme.char_width
    shape = node.shape

    if shape == "hub":
        d = max(112.0, text_w + 46.0)
        width = height = d
    elif shape.startswith("poly"):
        d = max(130.0, text_w + 60.0)
        width = height = d
    elif shape == "pill":
        height = 52.0
        width = max(140.0, text_w + theme.pad_x * 2)
    elif shape == "hex":
        height = 64.0
        width = max(160.0, text_w + theme.pad_x * 2 + 44.0)
    elif shape == "db":
        height = 78.0
        width = max(150.0, text_w + theme.pad_x * 2)
    elif shape == "diamond":
        height = 96.0
        width = max(160.0, text_w * 1.9 + 40.0)
    else:  # card
        height = theme.node_height
        width = max(MIN_WIDTH, text_w + theme.pad_x * 2)

    return replace(node, width=width, height=height)


def measure(diagram: Diagram, theme: Theme) -> Diagram:
    """Return a copy of ``diagram`` with every node and group measured."""
    nodes = tuple(measure_node(n, theme) for n in diagram.nodes)
    groups = tuple(
        measure_group(g, nodes) for g in diagram.groups
    )
    tables = tuple(measure_table(t, theme) for t in diagram.tables)
    return replace(diagram, nodes=nodes, groups=groups, tables=tables)


def measure_group(group: Group, nodes: tuple[Node, ...]) -> Group:
    """Size a group frame to fit its members in a grid."""
    members = [n for n in nodes if n.group == group.id]
    if not members:
        return replace(group, width=220.0, height=110.0)
    mw = max(m.width for m in members)
    mh = max(m.height for m in members)
    ncol = 1 if len(members) == 1 else 2
    nrow = math.ceil(len(members) / ncol)
    width = max(220.0, ncol * mw + (ncol + 1) * GROUP_MEMBER_GAP)
    height = GROUP_TITLE_BAR + nrow * mh + (nrow - 1) * GROUP_ROW_GAP + GROUP_PAD
    return replace(group, width=width, height=height)


def measure_table(table: Table, theme: Theme) -> Table:
    """Size a table from its header and rows."""
    ncol = table.columns
    if ncol == 0:
        return replace(table, width=TABLE_MIN_WIDTH, height=TABLE_TITLE_BAR)

    # Widest cell per column (header included).
    col_w = [TABLE_MIN_COL_W] * ncol
    all_rows = (table.header, *table.rows)
    for row in all_rows:
        for c in range(min(ncol, len(row))):
            text_w = len(row[c]) * theme.char_width + 2 * TABLE_CELL_PAD_X
            col_w[c] = max(col_w[c], text_w)

    width = max(TABLE_MIN_WIDTH, sum(col_w))
    header_h = TABLE_HEADER_H if table.header else 0.0
    height = TABLE_TITLE_BAR + header_h + len(table.rows) * TABLE_ROW_H
    return replace(table, width=width, height=height)
