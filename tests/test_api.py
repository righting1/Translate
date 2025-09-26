from fastapi.testclient import TestClient
from main import app


client = TestClient(app)


def test_health():
    resp = client.get("/api/v1/health")
    assert resp.status_code == 200
    assert resp.json().get("status") == "ok"


def test_greet():
    resp = client.get("/api/v1/greet/Alice")
    assert resp.status_code == 200
    assert "Hello Alice" in resp.json().get("message", "")


def test_translate_zh2en():
    payload = {"text": "你好，世界", "task": "zh2en"}
    resp = client.post("/api/translate/run", json=payload)
    assert resp.status_code == 200
    assert "result" in resp.json()


def test_translate_en2zh():
    payload = {"text": "Hello, world", "task": "en2zh"}
    resp = client.post("/api/translate/run", json=payload)
    assert resp.status_code == 200
    assert "result" in resp.json()


def test_summarize():
    payload = {"text": "a" * 300, "task": "summarize"}
    resp = client.post("/api/translate/run", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert len(data.get("result", "")) <= 123


