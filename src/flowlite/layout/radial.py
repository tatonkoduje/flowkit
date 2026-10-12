"""Radial layout: a central hub with members spread on a ring.

Selected by the compiler when the diagram declares a ``radial`` instruction. The
hub node is centered in the canvas; every other top-level item (standalone node
or group) is placed on a circle around it, evenly spaced starting at the
configured angle and proceeding clockwise. Group members stay inside their frame,
placed with the same grid helper the stack engine uses.

The engine only positions boxes. Face docking for polygon hubs is a rendering
concern (see :func:`flowlite.shapes.dock_anchor`).
"""

from __future__ import annotations

import math
from dataclasses import replace

from ..model import Diagram, Group, Node, Radial, Table
from ..themes import Theme
from .stack import TITLE_BLOCK, _place_members


def _half_extent(item: Node | Group | Table) -> float:
    """Largest half-dimension kept clear around an item's center."""
    return math.hypot(item.width, item.height) / 2


def _ring_positions(
    center_x: float, center_y: float, radius: float, count: int, start: float
) -> list[tuple[float, float]]:
    """Centers for ``count`` members on a ring, clockwise from ``start`` degrees."""
    if count == 0:
        return []
    if count == 1:
        angle = math.radians(start)
        return [(center_x + radius * math.cos(angle), center_y + radius * math.sin(angle))]
    step = 2 * math.pi / count
    base = math.radians(start)
    return [
        (
            center_x + radius * math.cos(base + i * step),
            center_y + radius * math.sin(base + i * step),
        )
        for i in range(count)
    ]


def layout(diagram: Diagram, theme: Theme) -> tuple[Diagram, int, int]:
    """Position the hub at center and members on a ring.

    Returns ``(positioned_diagram, canvas_width, canvas_height)``.
    """
    radial: Radial = diagram.radial  # type: ignore[assignment]
    margin = theme.margin
    hub = next((n for n in diagram.nodes if n.id == radial.hub), None)

    standalone = [
        n for n in diagram.nodes if not n.group and n.id != radial.hub
    ]
    members: list[Node | Group | Table] = [
        *standalone, *diagram.groups, *diagram.tables
    ]

    if hub is None:
        # No hub node: nothing to center on.
        return diagram, int(margin * 2), int(TITLE_BLOCK + margin)

    # Radius: explicit, or hub extent + gap + largest member extent.
    if radial.radius is not None:
        radius = radial.radius
    else:
        member_extent = max((_half_extent(m) for m in members), default=0.0)
        radius = _half_extent(hub) + radial.gap + member_extent

    # Canvas must fit the ring plus each item's own half extent, plus margin.
    ring_reach = radius + max((_half_extent(m) for m in members), default=0.0)
    half_w = ring_reach
    half_h = ring_reach
    canvas_w = int(2 * (margin + half_w))
    canvas_h = int(TITLE_BLOCK + 2 * half_h + margin)

    center_x = canvas_w / 2
    center_y = TITLE_BLOCK + half_h
    placed_hub = replace(hub, x=center_x - hub.width / 2, y=center_y - hub.height / 2)

    positions = _ring_positions(
        center_x, center_y, radius, len(members), radial.start
    )
    placed_nodes: list[Node] = [placed_hub]
    placed_groups: list[Group] = []
    placed_tables: list[Table] = []
    for item, (px, py) in zip(members, positions):
        x = px - item.width / 2
        y = py - item.height / 2
        if isinstance(item, Group):
            g = replace(item, x=x, y=y)
            placed_groups.append(g)
            placed_nodes.extend(_place_members(g, diagram.nodes))
        elif isinstance(item, Table):
            placed_tables.append(replace(item, x=x, y=y))
        else:
            placed_nodes.append(replace(item, x=x, y=y))

    positioned = replace(
        diagram,
        nodes=tuple(placed_nodes),
        groups=tuple(placed_groups),
        tables=tuple(placed_tables),
    )
    return positioned, canvas_w, canvas_h
