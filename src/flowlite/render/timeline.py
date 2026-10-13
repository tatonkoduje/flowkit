"""Timeline (Gantt) renderer.

Draws a dark (or themed) Gantt chart from a placed timeline: background, section
bands, weekly/monthly gridlines, section titles, bars and milestones, the bottom
axis, vertical markers and the title. Pure function of (timeline, layout, theme).
"""

from __future__ import annotations

from ..layout.timeline import PlacedItem, TimelineLayout
from ..model import Timeline, esc
from ..themes import Theme

BAR_RADIUS = 6.0
AXIS_FONT = 17.0  # larger date labels along the bottom (matches the reference)
GRID_FONT = 12.5


def render(timeline: Timeline, placed: TimelineLayout, theme: Theme) -> str:
    """Render ``timeline`` to a standalone SVG document string."""
    t = theme.timeline
    out: list[str] = []
    out.append(
        '<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" '
        'viewBox="0 0 %d %d" font-family="%s">'
        % (placed.width, placed.height, placed.width, placed.height, theme.font_family)
    )
    out.append(
        '<linearGradient id="tlbg" x1="0" y1="0" x2="1" y2="1">'
        '<stop offset="0" stop-color="%s"/><stop offset="1" stop-color="%s"/>'
        '</linearGradient>' % (theme.background_from, theme.background_to)
    )
    out.append(
        '<rect width="%d" height="%d" fill="url(#tlbg)"/>'
        % (placed.width, placed.height)
    )

    _title(out, timeline, theme, placed)

    # Section bands (alternating) across the plot area.
    for section in placed.sections:
        fill = t.row_band if section.index % 2 == 0 else t.row_band_alt
        out.append(
            '<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="%s"/>'
            % (placed.plot_x0, section.y, placed.plot_x1 - placed.plot_x0,
               section.height, fill)
        )

    _grid(out, placed, t)
    _section_labels(out, placed, t)
    _items(out, timeline, placed, theme)
    _axis(out, placed, t)
    _markers(out, placed, t)

    out.append("</svg>")
    return "\n".join(out)


def _title(out: list[str], timeline: Timeline, theme: Theme, placed: TimelineLayout) -> None:
    out.append(
        '<text x="%d" y="58" font-size="26" font-weight="700" fill="%s">%s</text>'
        % (int(theme.margin), theme.title, esc(timeline.title))
    )
    if timeline.subtitle:
        out.append(
            '<text x="%d" y="86" font-size="14" fill="%s">%s</text>'
            % (int(theme.margin), theme.subtitle, esc(timeline.subtitle))
        )


def _grid(out: list[str], placed: TimelineLayout, t) -> None:
    for tick in placed.grid_ticks:
        out.append(
            '<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" '
            'stroke-width="0.8"/>'
            % (tick.x, placed.plot_y0, tick.x, placed.plot_y1, t.gridline)
        )
        out.append(
            '<text x="%.1f" y="%.1f" text-anchor="middle" font-size="%.1f" '
            'fill="%s">%s</text>'
            % (tick.x, placed.plot_y1 - 6, GRID_FONT, t.grid_label, esc(tick.label))
        )


def _section_labels(out: list[str], placed: TimelineLayout, t) -> None:
    for section in placed.sections:
        cy = section.y + section.height / 2 + 4.5
        out.append(
            '<text x="%.1f" y="%.1f" font-size="14" font-weight="600" fill="%s">%s</text>'
            % (placed.plot_x0 - 16, cy, t.row_label, esc(section.title))
        )


def _items(out: list[str], timeline: Timeline, placed: TimelineLayout, theme: Theme) -> None:
    t = theme.timeline
    for pi in placed.items:
        item = pi.item
        section_color = theme.timeline.color(
            _section_color(timeline, item.section), t.row_band
        )
        fill = t.color(item.color, "") or section_color
        if not item.color:
            fill = _apply_state(fill, item.state)
        opacity = "1"
        dash = ""
        if item.state == "planned":
            opacity = "0.35"
            dash = ' stroke-dasharray="6 4"'
        if item.milestone:
            _milestone(out, pi, t.color(item.color, t.milestone), t)
            continue
        stroke = _darken(fill)
        out.append(
            '<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="%.1f" '
            'fill="%s" fill-opacity="%s" stroke="%s" stroke-width="1"%s/>'
            % (pi.x, pi.y, pi.w, pi.h, BAR_RADIUS, fill, opacity, stroke, dash)
        )
        _item_label(out, pi, t)


def _item_label(out: list[str], pi: PlacedItem, t) -> None:
    item = pi.item
    text = item.label
    # Estimate width (charWidth ~ 7.6 for the label font); place inside if it fits.
    est = len(text) * 7.6 + 16
    if est <= pi.w:
        out.append(
            '<text x="%.1f" y="%.1f" text-anchor="middle" font-size="12.5" '
            'font-weight="600" fill="%s">%s</text>'
            % (pi.x + pi.w / 2, pi.y + pi.h / 2 + 4.5, t.bar_text, esc(text))
        )
        note_x = pi.x + pi.w + 8
    else:
        out.append(
            '<text x="%.1f" y="%.1f" font-size="12.5" font-weight="600" fill="%s">%s</text>'
            % (pi.x + pi.w + 8, pi.y + pi.h / 2 + 4.5, t.row_label, esc(text))
        )
        note_x = pi.x + pi.w + 8 + len(text) * 7.6 + 8
    if item.note:
        out.append(
            '<text x="%.1f" y="%.1f" font-size="11" fill="%s">%s</text>'
            % (note_x, pi.y + pi.h / 2 + 4.0, t.note_text, esc(item.note))
        )


def _milestone(out: list[str], pi: PlacedItem, fill: str, t) -> None:
    cx, cy = pi.x + pi.w / 2, pi.y + pi.h / 2
    r = pi.w / 2
    pts = "%.1f,%.1f %.1f,%.1f %.1f,%.1f %.1f,%.1f" % (
        cx, cy - r, cx + r, cy, cx, cy + r, cx - r, cy
    )
    out.append(
        '<polygon points="%s" fill="%s" stroke="%s" stroke-width="1"/>'
        % (pts, fill, _darken(fill))
    )


def _axis(out: list[str], placed: TimelineLayout, t) -> None:
    out.append(
        '<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" '
        'stroke-width="1.4"/>'
        % (placed.plot_x0, placed.plot_y1, placed.plot_x1, placed.plot_y1, t.axis_line)
    )
    for tick in placed.axis_ticks:
        out.append(
            '<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" '
            'stroke-width="1.4"/>'
            % (tick.x, placed.plot_y1, tick.x, placed.plot_y1 + 6, t.axis_line)
        )
        out.append(
            '<text x="%.1f" y="%.1f" text-anchor="middle" font-size="%.1f" '
            'font-weight="600" fill="%s">%s</text>'
            % (tick.x, placed.plot_y1 + 30, AXIS_FONT, t.axis_label, esc(tick.label))
        )


def _markers(out: list[str], placed: TimelineLayout, t) -> None:
    for marker in placed.markers:
        out.append(
            '<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" '
            'stroke-width="1.6" stroke-dasharray="6 4"/>'
            % (marker.x, placed.plot_y0, marker.x, placed.plot_y1, "#F5CD47")
        )
        if marker.label:
            out.append(
                '<text x="%.1f" y="%.1f" font-size="15" font-weight="700" '
                'fill="%s">%s</text>'
                % (marker.x + 8, placed.plot_y0 - 7, "#F5CD47", esc(marker.label))
            )


def _section_color(timeline: Timeline, title: str) -> str:
    for section in timeline.sections:
        if section.title == title:
            return section.color
    return ""


def _apply_state(fill: str, state: str) -> str:
    """Mute a section colour for done items (keeps planned/active as-is)."""
    if state == "done":
        return _mix(fill, 0.65)
    return fill


def _mix(hex_color: str, factor: float) -> str:
    """Blend an ``#RRGGBB`` colour toward black by ``factor`` (0..1)."""
    if not hex_color.startswith("#") or len(hex_color) != 7:
        return hex_color
    r = int(int(hex_color[1:3], 16) * factor)
    g = int(int(hex_color[3:5], 16) * factor)
    b = int(int(hex_color[5:7], 16) * factor)
    return "#%02X%02X%02X" % (r, g, b)


def _darken(hex_color: str) -> str:
    return _mix(hex_color, 0.62)
