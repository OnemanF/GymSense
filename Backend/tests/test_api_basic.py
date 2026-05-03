from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_docs_available():
    response = client.get("/docs")
    assert response.status_code == 200


def test_measurements_history_endpoint_exists():
    response = client.get("/api/measurements/history?limit=5")
    assert response.status_code == 200