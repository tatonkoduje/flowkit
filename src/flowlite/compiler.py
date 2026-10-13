"""The FlowLite compiler pipeline: ``.fl`` source -> SVG text.

A convenience wrapper that runs the pure stages in order. Useful for tests and
embedding; the CLI uses it too.
"""

from __future__ import annotations

from dataclasses import replace

from .layout import auto, layered, radial, stack
from .layout import timeline as timeline_layout
from .measure import measure
from .model import Diagram
from .parser import parse
from .render import svg
from .render import timeline as timeline_render
from .themes import Theme, load_theme


def compile_diagram(source: str, theme: Theme | None = None) -> str:
    """Compile ``source`` text to an SVG string.

    If ``theme`` is omitted it is loaded from the theme named in the source.
    Returns the SVG as a string; warnings are ignored here (use the parser
    directly if you need them).
    """
    diagram, _warnings = parse(source)
    if theme is None:
        theme = load_theme(diagram.theme)
    if diagram.timeline is not None:
        placed = timeline_layout.layout(diagram.timeline, theme)
        return timeline_render.render(diagram.timeline, placed, theme)
    measured = measure(diagram, theme)
    if diagram.radial:
        engine = radial
    elif diagram.layers:
        engine = layered
    elif diagram.auto_layout:
        derived = auto.derive_layers(measured)
        positioned, width, height = layered.layout(
            replace(measured, layers=derived), theme
        )
        return svg.render(positioned, theme, width, height)
    else:
        engine = stack
    positioned, width, height = engine.layout(measured, theme)
    return svg.render(positioned, theme, width, height)


__all__ = ["compile_diagram", "Diagram", "Theme"]
