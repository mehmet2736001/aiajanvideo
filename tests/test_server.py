import pytest

pytest.importorskip("fastapi")
pytest.importorskip("httpx")

from fastapi.testclient import TestClient

from web import server


@pytest.fixture()
def client():
    return TestClient(server.app)


def test_index_and_health(client):
    assert client.get("/").status_code == 200
    h = client.get("/api/health").json()
    assert h["status"] == "ok" and "ffmpeg" in h


@pytest.mark.parametrize("slug", ["", "..", "../x", "a/b", "A B"])
def test_produce_rejects_bad_slug(client, slug):
    r = client.post("/api/produce", json={"project_slug": slug, "title": "t", "lines": ["a"]})
    assert r.status_code == 422
    assert r.json()["status"] == "error"


def test_produce_validates_body(client):
    assert client.post("/api/produce", json={"project_slug": "ok", "title": "t", "lines": []}).status_code == 422


def test_cors_only_for_localhost(client):
    ok = client.options("/api/state", headers={"Origin": "http://localhost:3000", "Access-Control-Request-Method": "GET"})
    assert ok.headers.get("access-control-allow-origin") == "http://localhost:3000"
    bad = client.options("/api/state", headers={"Origin": "https://evil.example", "Access-Control-Request-Method": "GET"})
    assert "access-control-allow-origin" not in bad.headers


def test_set_model_moves_to_front(client):
    r = client.post("/api/set_model", json={"model": "model-x"}).json()
    assert r["active_model"] == "model-x"


def test_error_log_roundtrip(client):
    client.post("/api/errors/clear")
    client.post("/api/errors/report", json={"error": {"message": "boom"}})
    assert client.get("/api/errors").json()["errors"][-1]["message"] == "boom"
    client.post("/api/errors/clear")
    assert client.get("/api/errors").json()["errors"] == []
