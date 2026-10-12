"""SVG renderer.

Draws the themed background, title, nodes (multiple shapes) and edges. Pure
function of (diagram, theme, width, height).
"""

from __future__ import annotations

from .. import icons, shapes
from ..measure import (
    TABLE_CELL_PAD_X,
    TABLE_HEADER_H,
    TABLE_MIN_COL_W,
    TABLE_ROW_H,
    TABLE_TITLE_BAR,
)
from ..model import Diagram, Group, Node, Table, esc
from ..themes import Theme

CORNER_RADIUS = 14.0
EDGE_WIDTH = 2.2
ICON_SIZE = 22.0  # rendered icon box (edge length) in px
ICON_LEFT_PAD = 16.0  # gap from the node's left edge to the icon
ICON_STACK_DY = 16.0  # vertical offset of the icon above a centered label


def render(diagram: Diagram, theme: Theme, width: int, height: int) -> str:
    """Render ``diagram`` to a standalone SVG document string."""
    out: list[str] = []
    out.append(
        '<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" '
        'viewBox="0 0 %d %d" font-family="%s">'
        % (width, height, width, height, theme.font_family)
    )
    out.append(_defs(theme))
    out.append('<rect width="%d" height="%d" fill="url(#bg)"/>' % (width, height))
    out.append(_title(diagram, theme))
    out.extend(_group_frames(diagram, theme))
    for table in diagram.tables:
        out.extend(_table(table, theme))
    out.extend(_edges(diagram, theme))
    for node in diagram.nodes:
        out.extend(_node(node, theme))
    out.append("</svg>")
    return "\n".join(out)


def _defs(theme: Theme) -> str:
    parts = ["<defs>"]
    parts.append(
        '<linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">'
        '<stop offset="0" stop-color="%s"/>'
        '<stop offset="1" stop-color="%s"/></linearGradient>'
        % (theme.background_from, theme.background_to)
    )
    for kind, (top, bottom) in sorted(theme.palette.items()):
        parts.append(
            '<linearGradient id="g-%s" x1="0" y1="0" x2="0" y2="1">'
            '<stop offset="0" stop-color="%s"/>'
            '<stop offset="1" stop-color="%s"/></linearGradient>' % (kind, top, bottom)
        )
    parts.append(
        '<filter id="cardShadow" x="-30%%" y="-30%%" width="160%%" height="160%%">'
        '<feDropShadow dx="0" dy="5" stdDeviation="7" '
        'flood-color="#000000" flood-opacity="0.35"/></filter>'
    )
    parts.append(
        '<marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" '
        'markerWidth="7" markerHeight="7" orient="auto">'
        '<path d="M 0 0 L 10 5 L 0 10 z" fill="%s"/></marker>' % theme.edge
    )
    parts.append(
        '<marker id="arrow-dot" viewBox="0 0 10 10" refX="5" refY="5" '
        'markerWidth="5" markerHeight="5">'
        '<circle cx="5" cy="5" r="4" fill="%s"/></marker>' % theme.edge
    )
    parts.append("</defs>")
    return "".join(parts)


def _title(diagram: Diagram, theme: Theme) -> str:
    parts = [
        '<text x="%d" y="58" font-size="26" font-weight="700" fill="%s">%s</text>'
        % (int(theme.margin), theme.title, esc(diagram.title))
    ]
    if diagram.subtitle:
        parts.append(
            '<text x="%d" y="86" font-size="14" fill="%s">%s</text>'
            % (int(theme.margin), theme.subtitle, esc(diagram.subtitle))
        )
    return "".join(parts)


def _by_id(diagram: Diagram) -> dict[str, Node | Group | Table]:
    lookup: dict[str, Node | Group | Table] = {n.id: n for n in diagram.nodes}
    lookup.update({g.id: g for g in diagram.groups})
    lookup.update({t.id: t for t in diagram.tables})
    return lookup


def _as_rect(item: Node | Group | Table) -> Node:
    """View a group or table as a rectangular node for edge geometry."""
    if isinstance(item, Group):
        return Node(
            id=item.id, label=item.title, kind=item.kind, shape="card",
            width=item.width, height=item.height, x=item.x, y=item.y,
        )
    if isinstance(item, Table):
        return Node(
            id=item.id, label=item.title, kind=item.kind, shape="card",
            width=item.width, height=item.height, x=item.x, y=item.y,
        )
    return item


def _group_frames(diagram: Diagram, theme: Theme) -> list[str]:
    """Translucent frames drawn under the nodes."""
    parts: list[str] = []
    for group in diagram.groups:
        top, _bottom = theme.kind_gradient(group.kind)
        parts.append(
            '<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="16" '
            'fill="%s" fill-opacity="0.10" stroke="%s" stroke-opacity="0.55" '
            'stroke-width="1.4" stroke-dasharray="7 6"/>'
            % (group.x, group.y, group.width, group.height, top, top)
        )
        parts.append(
            '<text x="%.1f" y="%.1f" font-size="13" font-weight="700" '
            'letter-spacing="0.5" fill="%s" fill-opacity="0.9">%s</text>'
            % (
                group.x + 16,
                group.y + 26,
                top,
                esc(group.title.upper()),
            )
        )
    return parts


def _table_columns(table: Table) -> list[float]:
    """Per-column widths, computed identically to measurement (deterministic)."""
    ncol = table.columns
    if ncol == 0:
        return []
    widths = [TABLE_MIN_COL_W] * ncol
    for row in (table.header, *table.rows):
        for c in range(min(ncol, len(row))):
            widths[c] = max(widths[c], len(row[c]) * 7.6 + 2 * TABLE_CELL_PAD_X)
    return widths


def _table(table: Table, theme: Theme) -> list[str]:
    """Draw a table: body, title bar, optional header row, rows and rules."""
    parts: list[str] = []
    top, bottom = theme.kind_gradient(table.kind)
    x, y, w = table.x, table.y, table.width
    h = table.height

    # Body.
    parts.append(
        '<g filter="url(#cardShadow)"><rect x="%.1f" y="%.1f" width="%.1f" '
        'height="%.1f" rx="12" fill="url(#g-%s)" fill-opacity="0.22" '
        'stroke="%s" stroke-opacity="0.5" stroke-width="1.2"/></g>'
        % (x, y, w, h, table.kind, top)
    )

    # Title bar.
    parts.append(
        '<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="12" '
        'fill="%s" fill-opacity="0.85"/>'
        % (x, y, w, TABLE_TITLE_BAR, top)
    )
    parts.append(
        '<text x="%.1f" y="%.1f" font-size="13" font-weight="700" '
        'letter-spacing="0.5" fill="#FFFFFF" fill-opacity="0.95">%s</text>'
        % (x + 16, y + 28, esc(table.title.upper()))
    )

    cols = _table_columns(table)
    cy = y + TABLE_TITLE_BAR
    if table.header:
        # Header row background.
        parts.append(
            '<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" '
            'fill="#FFFFFF" fill-opacity="0.06"/>'
            % (x, cy, w, TABLE_HEADER_H)
        )
        parts.extend(
            _table_row_text(table.header, cols, x, cy, TABLE_HEADER_H, "#FFFFFF", 0.9)
        )
        cy += TABLE_HEADER_H
        parts.append(_table_rule(x, cy, w, theme, strong=True))

    # Data rows.
    for i, row in enumerate(table.rows):
        ry = cy + i * TABLE_ROW_H
        if i % 2 == 1:
            parts.append(
                '<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" '
                'fill="#FFFFFF" fill-opacity="0.03"/>' % (x, ry, w, TABLE_ROW_H)
            )
        parts.extend(
            _table_row_text(row, cols, x, ry, TABLE_ROW_H, "#E2E8F0", 0.92)
        )
        if i < len(table.rows) - 1:
            parts.append(_table_rule(x, ry + TABLE_ROW_H, w, theme, strong=False))

    # Column dividers over the rows area.
    if len(cols) > 1:
        cx = x
        for cw in cols[:-1]:
            cx += cw
            parts.append(
                '<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="#FFFFFF" '
                'stroke-opacity="0.10" stroke-width="1"/>'
                % (cx, y + TABLE_TITLE_BAR, cx, y + h)
            )
    return parts


def _table_rule(x: float, y: float, w: float, theme: Theme, strong: bool) -> str:
    return (
        '<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="#FFFFFF" '
        'stroke-opacity="%s" stroke-width="1"/>'
        % (x, y, x + w, y, "0.22" if strong else "0.10")
    )


def _table_row_text(
    cells: tuple[str, ...],
    cols: list[float],
    x: float,
    y: float,
    row_h: float,
    color: str,
    opacity: float,
) -> list[str]:
    parts: list[str] = []
    cx = x
    baseline = y + row_h / 2 + 4.5
    for c, cw in enumerate(cols):
        text = cells[c] if c < len(cells) else ""
        if text:
            parts.append(
                '<text x="%.1f" y="%.1f" font-size="13" fill="%s" '
                'fill-opacity="%.2f">%s</text>'
                % (cx + TABLE_CELL_PAD_X, baseline, color, opacity, esc(text))
            )
        cx += cw
    return parts


def _edges(diagram: Diagram, theme: Theme) -> list[str]:
    lookup = _by_id(diagram)
    dock_hub = ""
    if diagram.radial is not None and diagram.radial.dock:
        dock_hub = diagram.radial.hub
    parts: list[str] = []
    for edge in diagram.edges:
        src = lookup.get(edge.src)
        dst = lookup.get(edge.dst)
        if src is None or dst is None:
            continue
        src = _as_rect(src)
        dst = _as_rect(dst)

        # Stroke style.
        if edge.style == "dashed":
            dash = ' stroke-dasharray="7 5"'
        else:
            dash = ""
        width = 3.4 if edge.style == "bold" else EDGE_WIDTH

        # Arrow head.
        if edge.arrow == "dot":
            marker = ' marker-end="url(#arrow-dot)"'
        elif edge.arrow == "none":
            marker = ""
        else:
            marker = ' marker-end="url(#arrow)"'

        scx, scy = shapes.center(src)
        dcx, dcy = shapes.center(dst)
        # When the two items are stacked (overlapping horizontally), connect
        # bottom-center to top-center so the edge meets the shape cleanly.
        overlap = min(src.x + src.width, dst.x + dst.width) - max(src.x, dst.x)
        stacked = overlap > 0.4 * min(src.width, dst.width) and abs(scy - dcy) > 0.6 * min(
            src.height, dst.height
        )

        if stacked:
            if scy <= dcy:  # src above dst
                x1, y1 = shapes.vertical_anchor(src, bottom=True)
                x2, y2 = shapes.vertical_anchor(dst, bottom=False)
            else:
                x1, y1 = shapes.vertical_anchor(src, bottom=False)
                x2, y2 = shapes.vertical_anchor(dst, bottom=True)
            c1x, c1y = x1, y1 + (30 if scy <= dcy else -30)
            c2x, c2y = x2, y2 + (-30 if scy <= dcy else 30)
            straight = edge.curve == "straight"
        else:
            if dock_hub and src.id == dock_hub:
                x1, y1 = shapes.dock_anchor(src, dcx, dcy)
            else:
                x1, y1 = shapes.anchor(src, dcx, dcy)
            if dock_hub and dst.id == dock_hub:
                x2, y2 = shapes.dock_anchor(dst, scx, scy)
            else:
                x2, y2 = shapes.anchor(dst, scx, scy)
            mid = max(60.0, (x2 - x1) / 2)
            c1x, c1y = x1 + mid, y1
            c2x, c2y = x2 - mid, y2
            straight = edge.curve == "straight"

        if straight:
            parts.append(
                '<path d="M %.1f %.1f L %.1f %.1f" fill="none" stroke="%s" '
                'stroke-width="%.1f" stroke-opacity="0.85"%s%s/>'
                % (x1, y1, x2, y2, theme.edge, width, dash, marker)
            )
            mx, my = (x1 + x2) / 2, (y1 + y2) / 2
        else:
            parts.append(
                '<path d="M %.1f %.1f C %.1f %.1f, %.1f %.1f, %.1f %.1f" '
                'fill="none" stroke="%s" stroke-width="%.1f" stroke-opacity="0.85"%s%s/>'
                % (x1, y1, c1x, c1y, c2x, c2y, x2, y2, theme.edge, width, dash, marker)
            )
            mx = (x1 + 3 * c1x + 3 * c2x + x2) / 8
            my = (y1 + 3 * c1y + 3 * c2y + y2) / 8

        if edge.label:
            parts.append(_edge_label(edge.label, mx, my, theme))
    return parts


def _edge_label(label: str, mx: float, my: float, theme: Theme) -> str:
    width = len(label) * 7.2 + 22
    return (
        '<rect x="%.1f" y="%.1f" width="%.1f" height="26" rx="13" '
        'fill="%s" fill-opacity="0.9"/>'
        '<text x="%.1f" y="%.1f" text-anchor="middle" font-size="12.5" '
        'fill="%s">%s</text>'
        % (
            mx - width / 2, my - 13, width,
            theme.label_background,
            mx, my + 4.5,
            theme.label_text, esc(label),
        )
    )


def _poly_points(verts: list[tuple[float, float]]) -> str:
    return " ".join("%.1f,%.1f" % (x, y) for x, y in verts)


def _icon(node: Node, cx: float, cy: float) -> str:
    """A node's icon, centered on ``(cx, cy)``, tinted white like the label."""
    path = icons.icon_path(node.icon)
    if path is None:
        return ""
    scale = ICON_SIZE / 24.0
    x = cx - ICON_SIZE / 2
    y = cy - ICON_SIZE / 2
    return (
        '<g transform="translate(%.1f %.1f) scale(%.4f)" fill="none" '
        'stroke="#FFFFFF" stroke-opacity="0.92" stroke-width="2" '
        'stroke-linecap="round" stroke-linejoin="round"><path d="%s"/></g>'
        % (x, y, scale, path)
    )


def _label(
    node: Node,
    font_size: float = 15.0,
    dy: float = 0.0,
    dx: float = 0.0,
) -> str:
    """A node's label, horizontally centered on the shape (offset by ``dx``)."""
    cx = node.x + node.width / 2 + dx
    return (
        '<text x="%.1f" y="%.1f" text-anchor="middle" font-size="%.1f" '
        'font-weight="600" fill="#FFFFFF">%s</text>'
        % (cx, node.y + node.height / 2 + 5.5 + dy, font_size, esc(node.label))
    )


def _wide_label_parts(
    node: Node, font_size: float = 15.0
) -> list[str]:
    """Body label for wide shapes: icon to the left when present, label centered
    in the remaining box."""
    cy = node.y + node.height / 2
    if not node.icon:
        return [_label(node, font_size=font_size)]
    left = node.x + ICON_LEFT_PAD
    icon = _icon(node, left + ICON_SIZE / 2, cy)
    # Center the label in the space to the right of the icon.
    right_edge = node.x + node.width - ICON_LEFT_PAD
    remaining_cx = (left + ICON_SIZE + right_edge) / 2
    dx = remaining_cx - (node.x + node.width / 2)
    return [icon, _label(node, font_size=font_size, dx=dx)]


def _centered_icon_parts(
    node: Node, font_size: float = 15.0
) -> list[str]:
    """Body label for compact shapes (hub/poly): icon above the label."""
    if not node.icon:
        return [_label(node, font_size=font_size)]
    cx = node.x + node.width / 2
    icon = _icon(node, cx, node.y + node.height / 2 - ICON_STACK_DY)
    return [icon, _label(node, font_size=font_size, dy=ICON_STACK_DY / 2 + 6.0)]


def _node(node: Node, theme: Theme) -> list[str]:
    """The SVG fragments for one node; wrapped in a link when ``link`` is set."""
    parts = _node_body(node, theme)
    if node.link:
        open_tag = (
            '<a href="%s" target="_blank" rel="noopener noreferrer">'
            % esc(node.link)
        )
        return [open_tag, *parts, "</a>"]
    return parts


def _node_body(node: Node, theme: Theme) -> list[str]:
    """Return the SVG fragments for one node (shape body + icon + label)."""
    kind = node.kind
    shape = node.shape
    parts: list[str] = []

    if shape == "hub":
        cx, cy = shapes.center(node)
        r = node.width / 2
        parts.append(
            '<circle cx="%.1f" cy="%.1f" r="%.1f" fill="none" stroke="%s" '
            'stroke-opacity="0.3" stroke-width="1.2" stroke-dasharray="3 4"/>'
            % (cx, cy, r + 9, theme.edge)
        )
        parts.append(
            '<g filter="url(#cardShadow)"><circle cx="%.1f" cy="%.1f" r="%.1f" '
            'fill="url(#g-%s)" stroke="#FFFFFF" stroke-opacity="0.3" '
            'stroke-width="1.5"/></g>' % (cx, cy, r, kind)
        )
        parts.extend(_centered_icon_parts(node))
        return parts

    if shape.startswith("poly"):
        parts.append(
            '<g filter="url(#cardShadow)"><polygon points="%s" fill="url(#g-%s)" '
            'stroke="#FFFFFF" stroke-opacity="0.25" stroke-width="1.4"/></g>'
            % (_poly_points(shapes.polygon_vertices(node)), kind)
        )
        parts.extend(_centered_icon_parts(node))
        return parts

    if shape == "diamond":
        cx, cy = shapes.center(node)
        w, h = node.width, node.height
        pts = "%.1f,%.1f %.1f,%.1f %.1f,%.1f %.1f,%.1f" % (
            cx, node.y + 4, node.x + w - 4, cy, cx, node.y + h - 4, node.x + 4, cy
        )
        parts.append(
            '<g filter="url(#cardShadow)"><polygon points="%s" fill="url(#g-%s)" '
            'stroke="#FFFFFF" stroke-opacity="0.25" stroke-width="1.2"/></g>'
            % (pts, kind)
        )
        parts.extend(_wide_label_parts(node, font_size=12.5))
        return parts

    if shape == "hex":
        parts.append(
            '<g filter="url(#cardShadow)"><polygon points="%s" fill="url(#g-%s)" '
            'stroke="#FFFFFF" stroke-opacity="0.2" stroke-width="1"/></g>'
            % (_poly_points(shapes.hex_vertices(node)), kind)
        )
        parts.extend(_wide_label_parts(node))
        return parts

    if shape == "db":
        x, y, w, h = node.x, node.y, node.width, node.height
        er = 11.0
        parts.append(
            '<g filter="url(#cardShadow)"><path d="M %.1f %.1f L %.1f %.1f '
            'A %.1f %.1f 0 0 0 %.1f %.1f L %.1f %.1f Z" fill="url(#g-%s)" '
            'stroke="#FFFFFF" stroke-opacity="0.2" stroke-width="1"/></g>'
            % (x, y + er, x, y + h - er, w / 2, er, x + w, y + h - er, x + w, y + er, kind)
        )
        parts.append(
            '<ellipse cx="%.1f" cy="%.1f" rx="%.1f" ry="%.1f" fill="%s" '
            'stroke="#FFFFFF" stroke-opacity="0.35" stroke-width="1"/>'
            % (x + w / 2, y + er, w / 2, er, theme.kind_gradient(kind)[0])
        )
        parts.extend(_wide_label_parts(node))
        return parts

    if shape == "pill":
        parts.append(
            '<g filter="url(#cardShadow)"><rect x="%.1f" y="%.1f" width="%.1f" '
            'height="%.1f" rx="%.1f" fill="url(#g-%s)" stroke="#FFFFFF" '
            'stroke-opacity="0.2" stroke-width="1"/></g>'
            % (node.x, node.y, node.width, node.height, node.height / 2, kind)
        )
        parts.extend(_wide_label_parts(node))
        return parts

    # card
    parts.append(
        '<g filter="url(#cardShadow)"><rect x="%.1f" y="%.1f" width="%.1f" '
        'height="%.1f" rx="%d" fill="url(#g-%s)" stroke="#FFFFFF" '
        'stroke-opacity="0.18" stroke-width="1"/></g>'
        % (node.x, node.y, node.width, node.height, int(CORNER_RADIUS), kind)
    )
    parts.extend(_wide_label_parts(node))
    return parts
