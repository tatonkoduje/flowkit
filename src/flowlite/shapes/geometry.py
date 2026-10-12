"""Shape geometry: vertices and border anchors.

Pure math on the model. Shared by the renderer and the edge logic so that "where
is a shape's border?" has exactly one answer.
"""

from __future__ import annotations

import math

from ..measure import poly_sides
from ..model import Node

PAD = 4.0  # small outward offset so connectors don't touch the stroke
#: Horizontal inset of the slanted hexagon sides (matches the renderer).
HEX_CUT = 20.0


def center(node: Node) -> tuple[float, float]:
    return node.x + node.width / 2, node.y + node.height / 2


def hex_vertices(node: Node, grow: float = 0.0) -> list[tuple[float, float]]:
    """Vertices of the flat-topped hexagon the renderer draws.

    Unlike a regular inscribed polygon, this hexagon uses the node's full width
    and height, so its border matches the drawn shape exactly.
    """
    x, y, w, h = node.x, node.y, node.width, node.height
    cut = HEX_CUT
    if grow:
        # Grow outward uniformly by nudging the box; keeps the cut constant.
        x, y, w, h = x - grow, y - grow, w + 2 * grow, h + 2 * grow
    return [
        (x + cut, y),
        (x + w - cut, y),
        (x + w, y + h / 2),
        (x + w - cut, y + h),
        (x + cut, y + h),
        (x, y + h / 2),
    ]


def polygon_vertices(node: Node, grow: float = 0.0) -> list[tuple[float, float]]:
    """Vertices of the node's polygon outline.

    ``hex`` returns the flat-topped hexagon actually drawn; every other polygonal
    shape is a regular polygon inscribed in the node's square box (even-sided
    polygons get a flat top).
    """
    if node.shape == "hex":
        return hex_vertices(node, grow)
    n = poly_sides(node.shape)
    cx, cy = center(node)
    r = min(node.width, node.height) / 2 + grow
    offset = -math.pi / 2 + (math.pi / n if n % 2 == 0 else 0.0)
    return [
        (cx + r * math.cos(offset + i * 2 * math.pi / n),
         cy + r * math.sin(offset + i * 2 * math.pi / n))
        for i in range(n)
    ]


def _ray_rect(node: Node, tx: float, ty: float, pad: float = PAD) -> tuple[float, float]:
    cx, cy = center(node)
    dx, dy = tx - cx, ty - cy
    if dx == 0 and dy == 0:
        return cx, cy
    sx = (node.width / 2 + pad) / abs(dx) if dx else math.inf
    sy = (node.height / 2 + pad) / abs(dy) if dy else math.inf
    s = min(sx, sy)
    return cx + dx * s, cy + dy * s


def _ray_circle(node: Node, tx: float, ty: float, pad: float = PAD) -> tuple[float, float]:
    cx, cy = center(node)
    dx, dy = tx - cx, ty - cy
    length = math.hypot(dx, dy) or 1.0
    r = node.width / 2 + pad
    return cx + dx / length * r, cy + dy / length * r


def _ray_polygon(node: Node, tx: float, ty: float, pad: float = PAD) -> tuple[float, float]:
    cx, cy = center(node)
    dx, dy = tx - cx, ty - cy
    length = math.hypot(dx, dy) or 1.0
    dx, dy = dx / length, dy / length
    verts = polygon_vertices(node, grow=pad)
    best = None
    nv = len(verts)
    for i in range(nv):
        x1, y1 = verts[i]
        x2, y2 = verts[(i + 1) % nv]
        denom = dx * (y2 - y1) - dy * (x2 - x1)
        if abs(denom) < 1e-9:
            continue
        t = ((x1 - cx) * (y2 - y1) - (y1 - cy) * (x2 - x1)) / denom
        u = ((x1 - cx) * dy - (y1 - cy) * dx) / denom
        if t > 0 and -1e-6 <= u <= 1 + 1e-6 and (best is None or t < best):
            best = t
    if best is None:
        return cx, cy
    return cx + dx * best, cy + dy * best


def anchor(node: Node, tx: float, ty: float) -> tuple[float, float]:
    """Border point of ``node`` facing the target point ``(tx, ty)``."""
    shape = node.shape
    if shape == "hub":
        return _ray_circle(node, tx, ty)
    if shape == "hex" or shape == "diamond" or shape.startswith("poly"):
        return _ray_polygon(node, tx, ty)
    return _ray_rect(node, tx, ty)


def vertical_anchor(node: Node, bottom: bool) -> tuple[float, float]:
    """Bottom-center or top-center of a node, on the real shape border."""
    cx, cy = center(node)
    shape = node.shape
    if shape == "hub":
        r = node.width / 2 + PAD
        return cx, cy + r if bottom else cy - r
    if shape == "hex":
        # Flat top/bottom edge of the drawn hexagon.
        return cx, node.y + node.height if bottom else node.y
    if shape == "diamond" or shape.startswith("poly"):
        apothem = (min(node.width, node.height) / 2) * math.cos(
            math.pi / poly_sides(shape)
        )
        return cx, cy + apothem if bottom else cy - apothem
    return cx, node.y + node.height if bottom else node.y


def is_polygon(shape: str) -> bool:
    """Whether ``shape`` has discrete flat faces suitable for docking."""
    return shape == "hex" or shape == "diamond" or shape.startswith("poly")


def dock_anchor(node: Node, tx: float, ty: float) -> tuple[float, float]:
    """Border point on a polygon ``node`` docked from the ray toward ``(tx, ty)``.

    The direction to the target selects the polygon **edge** whose outward
    normal best matches it; the returned point lies on that edge. Deterministic:
    ties break to the lower edge index. Non-polygons fall back to :func:`anchor`.
    """
    if not is_polygon(node.shape):
        return anchor(node, tx, ty)

    cx, cy = center(node)
    dx, dy = tx - cx, ty - cy
    length = math.hypot(dx, dy) or 1.0
    dx, dy = dx / length, dy / length

    verts = polygon_vertices(node, grow=PAD)
    nv = len(verts)

    # Candidate edges the ray actually crosses: the hit lies strictly ahead
    # (t > 0) and within the edge segment (0 <= u <= 1). Prefer the smallest t
    # (the true exit point); break ties by the edge whose outward normal best
    # matches the ray so a diagonal ray through a vertex still picks a face.
    best: tuple[float, float, int] | None = None
    for i in range(nv):
        x1, y1 = verts[i]
        x2, y2 = verts[(i + 1) % nv]
        ex, ey = x2 - x1, y2 - y1
        denom = dx * ey - dy * ex
        if abs(denom) < 1e-9:
            continue
        t = ((x1 - cx) * ey - (y1 - cy) * ex) / denom
        if t <= 1e-9:
            continue
        u = ((x1 - cx) * dy - (y1 - cy) * dx) / denom
        if not (-1e-6 <= u <= 1 + 1e-6):
            continue
        nx, ny = ey, -ex
        elen = math.hypot(ex, ey) or 1.0
        nx, ny = nx / elen, ny / elen
        if nx * ((x1 + x2) / 2 - cx) + ny * ((y1 + y2) / 2 - cy) < 0:
            nx, ny = -nx, -ny
        key = (t, -(nx * dx + ny * dy), i)
        if best is None or key < best:
            best = key

    if best is None:
        return anchor(node, tx, ty)
    t, _nd, i = best
    x1, y1 = verts[i]
    x2, y2 = verts[(i + 1) % nv]
    ex, ey = x2 - x1, y2 - y1
    denom = dx * ey - dy * ex
    t = ((x1 - cx) * ey - (y1 - cy) * ex) / denom
    return cx + dx * t, cy + dy * t
