"""Layered layout: ordered left-to-right columns.

Top-level items (standalone nodes and groups) are assigned to columns by the
``layer <n>: ids`` instruction. Columns are laid out left-to-right in ascending
``<n>`` order; items in no layer go to a trailing column. Each column is
centered vertically. Group members stay inside their frame, placed with the same
grid helper the stack engine uses.

Selected by the compiler when the diagram declares any ``layer``.
"""

from __future__ import annotations

from dataclasses import replace

from ..model import Diagram, Group, Layer, Node, Table
from ..themes import Theme
from .stack import TITLE_BLOCK, _place_members

# Horizontal gap between adjacent columns.
COLUMN_GAP = 90.0


def _assign_columns(
    items: list[Node | Group | Table], layers: tuple[Layer, ...]
) -> tuple[dict[int, list[Node | Group | Table]], list[Node | Group | Table]]:
    """Bucket top-level items by column index; return buckets + unassigned."""
    by_id: dict[str, Node | Group | Table] = {it.id: it for it in items}
    buckets: dict[int, list[Node | Group | Table]] = {}
    placed: set[str] = set()
    for layer in layers:
        for item_id in layer.ids:
            item = by_id.get(item_id)
            if item is None:
                continue
            buckets.setdefault(layer.index, []).append(item)
            placed.add(item_id)
    unassigned = [it for it in items if it.id not in placed]
    return buckets, unassigned


def layout(diagram: Diagram, theme: Theme) -> tuple[Diagram, int, int]:
    """Position items as ordered columns.

    Returns ``(positioned_diagram, canvas_width, canvas_height)``.
    """
    standalone = [n for n in diagram.nodes if not n.group]
    items: list[Node | Group | Table] = [
        *standalone, *diagram.groups, *diagram.tables
    ]
    margin = theme.margin
    gap = theme.row_gap

    if not items:
        return diagram, int(margin * 2), int(TITLE_BLOCK + margin)

    buckets, unassigned = _assign_columns(items, diagram.layers)

    # Ordered column list: ascending layer index, then the trailing column.
    columns: list[list[Node | Group | Table]] = [
        buckets[i] for i in sorted(buckets)
    ]
    if unassigned:
        columns.append(unassigned)
    columns = [c for c in columns if c]

    col_widths = [max(it.width for it in col) for col in columns]
    col_heights = [
        sum(it.height for it in col) + gap * (len(col) - 1) for col in columns
    ]
    canvas_w = int(margin * 2 + sum(col_widths) + COLUMN_GAP * (len(columns) - 1))
    body_h = max(col_heights, default=0)
    canvas_h = int(TITLE_BLOCK + body_h + margin)

    x = margin
    placed_nodes: list[Node] = []
    placed_groups: list[Group] = []
    placed_tables: list[Table] = []
    for col, col_w, col_h in zip(columns, col_widths, col_heights):
        y = TITLE_BLOCK + (body_h - col_h) / 2
        for it in col:
            dx = x + (col_w - it.width) / 2
            if isinstance(it, Group):
                g = replace(it, x=dx, y=y)
                placed_groups.append(g)
                placed_nodes.extend(_place_members(g, diagram.nodes))
            elif isinstance(it, Table):
                placed_tables.append(replace(it, x=dx, y=y))
            else:
                placed_nodes.append(replace(it, x=dx, y=y))
            y += it.height + gap
        x += col_w + COLUMN_GAP

    positioned = replace(
        diagram,
        nodes=tuple(placed_nodes),
        groups=tuple(placed_groups),
        tables=tuple(placed_tables),
    )
    return positioned, canvas_w, canvas_h
