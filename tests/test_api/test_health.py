# tests/test_api/test_health.py

import pytest
from fastapi.testclient import TestClient


def test_health_endpoint(test_client: TestClient):
    """Test that the health check endpoint returns correct response."""
    response = test_client.get("/health")
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "app" in data
    assert data["app"] == "Leads Service Test"
