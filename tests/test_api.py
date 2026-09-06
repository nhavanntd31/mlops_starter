import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient


@pytest.fixture
def client():
    with patch("app.model_loader.model_holder") as mock_holder:
        mock_holder.model = MagicMock()
        mock_holder.model_name = "house-price-model"
        mock_holder.model_version = "1"
        mock_holder.features = ["area", "bedrooms", "bathrooms", "age", "floors", "location_encoded"]
        mock_holder.predict.return_value = 450000.0

        from app.main import app
        yield TestClient(app)


def test_health(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"


def test_predict(client):
    payload = {
        "features": {
            "area": 2000,
            "bedrooms": 3,
            "bathrooms": 2.25,
            "age": 30,
            "floors": 1.0,
            "location_encoded": 20,
        }
    }
    resp = client.post("/predict", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert "prediction" in data
    assert "latency_ms" in data


def test_model_info(client):
    resp = client.get("/model-info")
    assert resp.status_code == 200
    data = resp.json()
    assert data["model_name"] == "house-price-model"
