"""FlowLite shape geometry.

Re-exports the geometry helpers so callers can ``from . import shapes`` and use
``shapes.anchor(...)`` etc.
"""

from __future__ import annotations

from .geometry import (
    anchor,
    center,
    dock_anchor,
    hex_vertices,
    is_polygon,
    polygon_vertices,
    vertical_anchor,
)

__all__ = [
    "anchor",
    "center",
    "dock_anchor",
    "hex_vertices",
    "is_polygon",
    "polygon_vertices",
    "vertical_anchor",
]
