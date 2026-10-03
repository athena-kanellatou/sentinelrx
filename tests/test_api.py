from fastapi.testclient import TestClient

from sentinelrx.api import app

client = TestClient(app)

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_analyze_rejects_non_bundle():
    response = client.post("/analyze", json={"resourceType": "Patient"})
    assert response.status_code == 400
