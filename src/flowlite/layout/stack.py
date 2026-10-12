"""Stack layout: top-level items top-to-bottom, centered, in declaration order.

Top-level items are standalone nodes and groups. Group members are excluded from
the top-level stack and placed in a grid inside their frame. A deliberately naive
placeholder engine — the seam that ``layer``/``radial``/auto-layout will replace.
"""

from __future__ import annotations

from dataclasses import replace

from ..measure import GROUP_MEMBER_GAP, GROUP_ROW_GAP, GROUP_TITLE_BAR
from ..model import Diagram, Group, Node, Table
from ..themes import Theme

# Canvas title block height (above the first item).
TITLE_BLOCK = 130.0


def _grid_positions(members: list[Node], center_x: float, top_y: float) -> list[Node]:
    """Place members in a centered 2-column grid.

    ``center_x`` is the grid's horizontal center; ``top_y`` its top edge.
    """
    if not members:
        return []
    mw = max(m.width for m in members)
    mh = max(m.height for m in members)
    ncol = 1 if len(members) == 1 else 2

    grid_w = ncol * mw + (ncol - 1) * GROUP_MEMBER_GAP
    left = center_x - grid_w / 2
    top = top_y

    placed: list[Node] = []
    for i, m in enumerate(members):
        r, c = divmod(i, ncol)
        cx = left + c * (mw + GROUP_MEMBER_GAP)
        cy = top + r * (mh + GROUP_ROW_GAP)
        placed.append(
            replace(
                m,
                x=cx + (mw - m.width) / 2,
                y=cy + (mh - m.height) / 2,
            )
        )
    return placed


def _place_members(group: Group, nodes: tuple[Node, ...]) -> list[Node]:
    """Place the members belonging to ``group`` inside its frame."""
    members = [n for n in nodes if n.group == group.id]
    if not members:
        return []
    # Body center-x and body top (below the title bar).
    body_center_x = group.x + group.width / 2
    body_top = group.y + GROUP_TITLE_BAR
    return _grid_positions(members, body_center_x, body_top)


def layout(diagram: Diagram, theme: Theme) -> tuple[Diagram, int, int]:
    """Position groups and top-level nodes as a centered vertical stack.

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

    col_width = max(it.width for it in items)
    total_h = sum(it.height for it in items) + gap * (len(items) - 1)

    y = TITLE_BLOCK
    placed_nodes: list[Node] = []
    placed_groups: list[Group] = []
    placed_tables: list[Table] = []
    for it in items:
        dx = margin + (col_width - it.width) / 2
        if isinstance(it, Group):
            g = replace(it, x=dx, y=y)
            placed_groups.append(g)
            placed_nodes.extend(_place_members(g, diagram.nodes))
        elif isinstance(it, Table):
            placed_tables.append(replace(it, x=dx, y=y))
        else:
            placed_nodes.append(replace(it, x=dx, y=y))
        y += it.height + gap

    canvas_w = int(margin * 2 + col_width)
    canvas_h = int(TITLE_BLOCK + total_h + margin)
    positioned = replace(
        diagram,
        nodes=tuple(placed_nodes),
        groups=tuple(placed_groups),
        tables=tuple(placed_tables),
    )
    return positioned, canvas_w, canvas_h
