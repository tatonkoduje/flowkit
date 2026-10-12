"""Vendored icon set.

Icons are **data**, not code: a small curated subset of `lucide
<https://lucide.dev>`_ (ISC) lives in ``icons/lucide.json`` as ``name -> path d``
for a 24x24 viewBox. Nothing here depends on third-party packages.
"""

from __future__ import annotations

import json
from pathlib import Path

# Repository root: src/flowlite/icons.py -> ../../icons
ICONS_DIR = Path(__file__).resolve().parents[2] / "icons"
ICONS_FILE = ICONS_DIR / "lucide.json"

_cache: dict[str, str] | None = None


def _load() -> dict[str, str]:
    global _cache
    if _cache is None:
        try:
            data = json.loads(ICONS_FILE.read_text(encoding="utf-8"))
            _cache = {name: str(d) for name, d in data["icons"].items()}
        except (OSError, json.JSONDecodeError, KeyError, TypeError):
            _cache = {}
    return _cache


def all_icons() -> dict[str, str]:
    """Return the vendored icon set as ``name -> path d``."""
    return dict(_load())


def icon_path(name: str) -> str | None:
    """Path data for ``name``, or ``None`` if the icon is not vendored."""
    return _load().get(name)
