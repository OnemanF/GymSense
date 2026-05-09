from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_invalid_measurement_is_rejected():
    payload = {
        "deviceId": "esp32-test",
        "temperature": 182.0,
        "humidity": 100.0,
        "pressure": -172.0,
        "altitude": 0,
        "lightRaw": 0,
        "lightPercent": 0,
        "lightCategory": "Dark"
    }

    response = client.post("/api/measurements", json=payload)

    assert response.status_code == 422
    assert response.json()["detail"] == "Invalid sensor reading. Measurement was not saved."