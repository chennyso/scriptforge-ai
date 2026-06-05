from fastapi.testclient import TestClient

from app.main import app


def test_long_sample_endpoint_is_available():
    client = TestClient(app)
    response = client.get("/api/samples/alice-wonderland")
    assert response.status_code == 200
    body = response.json()
    assert "CHAPTER I" in body["text"]
    assert len(body["text"]) > 100000
