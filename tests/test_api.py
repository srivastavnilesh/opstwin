"""Phase 5: API integration tests using FastAPI TestClient."""
from fastapi.testclient import TestClient

from src.serving.api import app


def test_health():
    with TestClient(app) as client:
        res = client.get("/health")
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "healthy"
        assert data["model_loaded"] is True


def test_predict():
    with TestClient(app) as client:
        payload = {
            "assets": [
                {
                    "avg_vibration": 2.5,
                    "std_vibration": 0.5,
                    "avg_power": 8.0,
                    "outlier_count": 250,
                    "wo_count": 100,
                    "sla_breach_count": 10,
                },
                {
                    "avg_vibration": 1.0,
                    "std_vibration": 0.1,
                    "avg_power": 4.0,
                    "outlier_count": 10,
                    "wo_count": 2,
                    "sla_breach_count": 0,
                },
            ]
        }
        res = client.post("/predict", json=payload)
        assert res.status_code == 200
        data = res.json()
        assert len(data["predictions"]) == 2
        assert len(data["probabilities"]) == 2
        # The first asset is high-risk, the second is healthy.
        # Its probability score MUST be higher.
        assert data["probabilities"][0] > data["probabilities"][1]