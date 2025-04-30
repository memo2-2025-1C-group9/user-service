import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_get_health():
    """Prueba que devuelva status ok el endpoint health"""

    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
