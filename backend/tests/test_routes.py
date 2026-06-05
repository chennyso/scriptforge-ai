from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app


def test_generate_route_with_public_domain_sample():
    client = TestClient(app)
    text = Path("../examples/public-domain-novel.md").read_text(encoding="utf-8")
    response = client.post(
        "/api/generate",
        json={
            "text": text,
            "settings": {
                "script_type": "screenplay",
                "style": "conflict_plus",
                "target_scene_count": 6,
                "narration_level": "light",
                "dialogue_density": "medium",
            },
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["validation"]["valid"] is True
    assert body["provider"] == "rule-engine"
