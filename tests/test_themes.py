"""Theme loading tests."""

from __future__ import annotations

import json

import pytest

from flowlite.themes import ThemeError, load_theme


def test_load_midnight():
    theme = load_theme("midnight")
    assert theme.name == "midnight"
    assert theme.kind_gradient("store") != theme.kind_gradient("default")


def test_load_light():
    theme = load_theme("light")
    assert theme.name == "light"


def test_unknown_theme_raises_with_name():
    with pytest.raises(ThemeError) as exc:
        load_theme("does-not-exist")
    assert "does-not-exist" in str(exc.value)


def test_malformed_theme_raises(tmp_path):
    bad = tmp_path / "bad.json"
    bad.write_text(json.dumps({"name": "bad"}), encoding="utf-8")
    with pytest.raises(ThemeError):
        load_theme("bad", themes_dir=tmp_path)


def test_unknown_kind_falls_back_to_default():
    theme = load_theme("midnight")
    assert theme.kind_gradient("nonsense") == theme.kind_gradient("default")
