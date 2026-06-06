from fastapi.testclient import TestClient

from app.main import app


def test_long_sample_endpoint_is_available():
    client = TestClient(app)
    response = client.get("/api/samples/alice-wonderland")
    assert response.status_code == 200
    body = response.json()
    assert "CHAPTER I" in body["text"]
    assert len(body["text"]) > 100000


def test_chinese_long_sample_endpoint_is_available():
    client = TestClient(app)
    response = client.get("/api/samples/journey-west")
    assert response.status_code == 200
    body = response.json()
    assert "第一回" in body["text"]
    assert len(body["text"]) > 500000


def test_guofeng_webnovel_sample_endpoint_is_available():
    client = TestClient(app)
    response = client.get("/api/samples/guofeng-webnovel")
    assert response.status_code == 200
    body = response.json()
    assert "第1章" in body["text"]
    assert len(body["text"]) > 500000
