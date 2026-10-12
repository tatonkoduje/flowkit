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

    def kind_gradient(self, kind: str) -> tuple[str, str]:
        """Gradient pair for ``kind``, falling back to ``default``."""
        return self.palette.get(kind, self.palette["default"])


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
        )
    except (KeyError, IndexError, TypeError, ValueError) as exc:
        raise ThemeError(f"malformed theme {name}: {exc}") from exc
