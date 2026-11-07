import pytest

from core import director_brain as db


class Resp:
    def __init__(self, code, text="merhaba"):
        self.status_code = code
        self._text = text

    def json(self):
        return {"candidates": [{"content": {"parts": [{"text": self._text}]}}]}


@pytest.fixture()
def brain(tmp_path, monkeypatch):
    monkeypatch.setattr(db, "HISTORY_FILE", str(tmp_path / "h.json"))
    monkeypatch.setattr(db, "ARCHIVES_DIR", str(tmp_path))
    monkeypatch.setattr(db, "KEYS_FILE", str(tmp_path / "yok.json"))
    monkeypatch.setenv("GEMINI_API_KEYS", "k1,k2")
    monkeypatch.setenv("GEMINI_MODELS", "m1,m2")
    return db.DirectorBrain()


def test_429_rotates_key_then_succeeds(brain, monkeypatch):
    seen = []

    def post(url, json=None, headers=None, timeout=None):
        seen.append((url.split("/models/")[1].split(":")[0], headers["x-goog-api-key"]))
        return Resp(429) if len(seen) == 1 else Resp(200, "selam")

    monkeypatch.setattr(db.requests, "post", post)
    r = brain.chat("merhaba")
    assert r["reply"] == "selam" and r["model_used"] == "m1"
    assert [k for _, k in seen] == ["k1", "k2"]  # anahtar sızıntısı URL'de değil başlıkta
    assert len(brain.get_history()) == 3  # karşılama + kullanıcı + model


def test_404_disables_model_and_falls_to_next(brain, monkeypatch):
    def post(url, json=None, headers=None, timeout=None):
        return Resp(404) if "/m1:" in url else Resp(200, "m2 cevabı")

    monkeypatch.setattr(db.requests, "post", post)
    r = brain.chat("selam")
    assert r["model_used"] == "m2" and "m1" in brain._dead_models
    assert "m1" not in brain.get_status()["models"]


def test_no_keys_gives_clear_message(tmp_path, monkeypatch):
    monkeypatch.setattr(db, "HISTORY_FILE", str(tmp_path / "h.json"))
    monkeypatch.setattr(db, "KEYS_FILE", str(tmp_path / "yok.json"))
    monkeypatch.delenv("GEMINI_API_KEYS", raising=False)
    r = db.DirectorBrain().chat("merhaba")
    assert r["degraded"] and "API anahtarı yok" in r["reply"]


def test_prefer_model_and_history_cap(brain, monkeypatch):
    assert brain.prefer_model("m2") and brain.model_chain[0] == "m2"
    assert not brain.prefer_model("m2")
    monkeypatch.setattr(db, "MAX_HISTORY_MESSAGES", 5)
    monkeypatch.setattr(db.requests, "post", lambda *a, **k: Resp(200, "ok"))
    for i in range(6):
        brain.chat(f"mesaj {i}")
    assert len(brain.get_history()) <= 5
