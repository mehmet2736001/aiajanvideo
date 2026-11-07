import json
import os

import pytest

from core.utils import InvalidSlugError, atomic_write_json, read_json, safe_join, validate_slug


@pytest.mark.parametrize("slug", ["hud-112", "olum_son_mu", "a", "tefekkur-video-2"])
def test_valid_slugs(slug):
    assert validate_slug(slug) == slug


@pytest.mark.parametrize("slug", ["", ".", "..", "../x", "a/b", "a\\b", "-x", "A", "a b", "x" * 65, None, 5])
def test_invalid_slugs(slug):
    with pytest.raises(InvalidSlugError):
        validate_slug(slug)


def test_safe_join_blocks_escape(tmp_path):
    assert safe_join(str(tmp_path), "ok").startswith(str(tmp_path))
    with pytest.raises(InvalidSlugError):
        safe_join(str(tmp_path), "..", "evil")


def test_atomic_write_and_read(tmp_path):
    p = tmp_path / "d" / "x.json"
    atomic_write_json(str(p), {"a": "ğüş"})
    assert json.loads(p.read_text(encoding="utf-8")) == {"a": "ğüş"}
    assert not [f for f in os.listdir(p.parent) if f.endswith(".tmp")]
    assert read_json(str(tmp_path / "yok.json"), []) == []
