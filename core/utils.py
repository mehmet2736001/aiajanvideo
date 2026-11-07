"""Ortak yardımcılar: slug doğrulama, güvenli yol birleştirme, atomik JSON yazımı."""
import json
import os
import re
import tempfile
from typing import Any

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

SLUG_RE = re.compile(r"^[a-z0-9][a-z0-9_-]{0,63}$")


class InvalidSlugError(ValueError):
    """project_slug güvenli biçimde değil."""


def validate_slug(slug: str) -> str:
    """Yalnızca küçük harf, rakam, '-' ve '_' içeren, 64 karakteri aşmayan slug kabul edilir.

    Boş değer, '.', '..', '/', '\\' gibi yol öğeleri reddedilir.
    """
    if not isinstance(slug, str) or not SLUG_RE.match(slug):
        raise InvalidSlugError(
            "project_slug yalnızca küçük harf, rakam, '-' ve '_' içerebilir "
            "(en fazla 64 karakter, harf/rakamla başlamalı)."
        )
    return slug


def safe_join(base: str, *parts: str) -> str:
    """base altında kalmayı garanti eden yol birleştirme."""
    base_abs = os.path.abspath(base)
    target = os.path.abspath(os.path.join(base_abs, *parts))
    if target != base_abs and not target.startswith(base_abs + os.sep):
        raise InvalidSlugError("Yol, izin verilen klasörün dışına çıkıyor.")
    return target


def atomic_write_json(path: str, data: Any) -> None:
    """Yarım yazılmış dosya bırakmamak için geçici dosya + os.replace kullanır."""
    directory = os.path.dirname(os.path.abspath(path))
    os.makedirs(directory, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=directory, suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        os.replace(tmp, path)
    except Exception:
        if os.path.exists(tmp):
            os.remove(tmp)
        raise


def read_json(path: str, default: Any) -> Any:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return default
