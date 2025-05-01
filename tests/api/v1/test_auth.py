"""Tests for auth endpoints."""
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_login_access_token():
    """Test login access token endpoint."""
    response = client.post(
        "/api/v1/auth/login/access-token",
        data={
            "username": "test@example.com",
            "password": "test123",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_access_token_invalid_credentials():
    """Test login access token endpoint with invalid credentials."""
    response = client.post(
        "/api/v1/auth/login/access-token",
        data={
            "username": "test@example.com",
            "password": "wrong_password",
        },
    )
    assert response.status_code == 401


def test_test_token():
    """Test test token endpoint."""
    # First get a token
    response = client.post(
        "/api/v1/auth/login/access-token",
        data={
            "username": "test@example.com",
            "password": "test123",
        },
    )
    assert response.status_code == 200
    data = response.json()
    token = data["access_token"]

    # Then test the token
    response = client.post(
        "/api/v1/auth/login/test-token",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test@example.com" 