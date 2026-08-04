from fastapi.testclient import TestClient

from hook_intelligence.api.main import app


def test_health_returns_versioned_ready_status():
    response = TestClient(app).get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ready",
        "service": "hook-intelligence",
        "version": "0.1.0",
        "ai_enabled": False,
    }
