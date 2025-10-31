""
Tests for the main FastAPI application.
"""
from fastapi.testclient import TestClient
from {{project_name}}.main import app

client = TestClient(app)

def test_read_root():
    ""Test the root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()
    assert "{{project_name}}" in response.json()["message"]
