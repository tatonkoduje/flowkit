"""Theme loading.

A theme is a JSON data file in ``themes/`` selected by name in the source
(``theme <name>``). Render code reads colors and design tokens from here and
never hard-codes them.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

# Repository root: src/flowlite/themes.py -> ../../themes
THEMES_DIR = Path(__file__).resolve().parents[2] / "themes"


class ThemeError(Exception):
    """Raised when a theme is missing or malformed."""


@dataclass(frozen=True)
class TimelineTheme:
    """Colours for the timeline (Gantt) renderer."""

    row_band: str
    row_band_alt: str
    row_label: str
    gridline: str
    grid_label: str
    axis_line: str
    axis_label: str
    bar_text: str
    note_text: str
    milestone: str
    palette: dict[str, str]

    def color(self, name: str, default: str = "") -> str:
        """Resolve a palette name or raw ``#hex``; ``default`` if unknown/empty."""
        if not name:
            return default
        if name.startswith("#"):
            return name
        return self.palette.get(name, default)


@dataclass(frozen=True)
class Theme:
    """A resolved theme: colors, palette and design tokens."""

    name: str
    background_from: str
    background_to: str
    title: str
    subtitle: str
    edge: str
    label_background: str
    label_text: str
    palette: dict[str, tuple[str, str]]
    # Design tokens.
    char_width: float
    node_height: float
    pad_x: float
    row_gap: float
    top: float
    margin: float
    font_family: str
    timeline: TimelineTheme

    def kind_gradient(self, kind: str) -> tuple[str, str]:
        """Gradient pair for ``kind``, falling back to ``default``."""
        return self.palette.get(kind, self.palette["default"])


DEFAULT_TIMELINE = {
    "rowBand": "#242B33",
    "rowBandAlt": "#1F262E",
    "rowLabel": "#C7D2DD",
    "gridline": "#3A424D",
    "gridLabel": "#8A97A4",
    "axisLine": "#55636F",
    "axisLabel": "#C7D2DD",
    "barText": "#FFFFFF",
    "noteText": "#B6C2CF",
    "milestone": "#B6C2CF",
    "palette": {
        "slate": "#4C5966",
        "blue": "#1D7AFC",
        "teal": "#2898BD",
        "green": "#22A06B",
        "lime": "#6A9A23",
        "amber": "#F5CD47",
        "rose": "#E5484D",
    },
}


def _load_timeline(data: dict) -> TimelineTheme:
    """Build the timeline colour block, filling gaps from DEFAULT_TIMELINE."""
    block = data.get("timeline", {})
    merged = {**DEFAULT_TIMELINE, **block}
    palette = {**DEFAULT_TIMELINE["palette"], **block.get("palette", {})}
    return TimelineTheme(
        row_band=merged["rowBand"],
        row_band_alt=merged["rowBandAlt"],
        row_label=merged["rowLabel"],
        gridline=merged["gridline"],
        grid_label=merged["gridLabel"],
        axis_line=merged["axisLine"],
        axis_label=merged["axisLabel"],
        bar_text=merged["barText"],
        note_text=merged["noteText"],
        milestone=merged["milestone"],
        palette=palette,
    )


def load_theme(name: str, themes_dir: Path | None = None) -> Theme:
    """Load theme ``name`` from ``themes_dir`` (default: ``themes/``).

    Raises :class:`ThemeError` if the theme does not exist or is malformed.
    """
    base = themes_dir or THEMES_DIR
    path = base / f"{name}.json"
    if not path.exists():
        raise ThemeError(f"unknown theme: {name} (no file {path})")

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ThemeError(f"cannot read theme {name}: {exc}") from exc

    try:
        palette = {
            kind: (colors[0], colors[1]) for kind, colors in data["palette"].items()
        }
        bg = data["background"]
        tokens = data["tokens"]
        return Theme(
            name=data.get("name", name),
            background_from=bg["from"],
            background_to=bg["to"],
            title=data["title"],
            subtitle=data["subtitle"],
            edge=data["edge"],
            label_background=data.get("labelBackground", "#1E293B"),
            label_text=data.get("labelText", "#E2E8F0"),
            palette=palette,
            char_width=float(tokens["charWidth"]),
            node_height=float(tokens["nodeHeight"]),
            pad_x=float(tokens["padX"]),
            row_gap=float(tokens["rowGap"]),
            top=float(tokens["top"]),
            margin=float(tokens["margin"]),
            font_family=tokens["fontFamily"],
            timeline=_load_timeline(data),
        )
    except (KeyError, IndexError, TypeError, ValueError) as exc:
        raise ThemeError(f"malformed theme {name}: {exc}") from exc
