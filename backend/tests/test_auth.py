"""Tests for authentication endpoints: login, refresh, /auth/me, unauthorized."""
import pytest


# ---------------------------------------------------------------------------
# Login
# ---------------------------------------------------------------------------

def test_login_success(client):
    resp = client.post(
        "/api/v1/auth/login",
        data={"username": "admin", "password": "admin123"},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert "access_token" in body
    assert "refresh_token" in body
    assert body["username"] == "admin"
    assert body["role"] == "admin"


def test_login_wrong_password(client):
    resp = client.post(
        "/api/v1/auth/login",
        data={"username": "admin", "password": "wrongpass"},
    )
    assert resp.status_code == 401


def test_login_unknown_user(client):
    resp = client.post(
        "/api/v1/auth/login",
        data={"username": "nobody", "password": "x"},
    )
    assert resp.status_code == 401


# ---------------------------------------------------------------------------
# /auth/me
# ---------------------------------------------------------------------------

def test_get_me_success(client, admin_token):
    resp = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["username"] == "admin"
    assert body["role"] == "admin"


def test_get_me_no_token(client):
    resp = client.get("/api/v1/auth/me")
    assert resp.status_code == 401


def test_get_me_invalid_token(client):
    resp = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": "Bearer this.is.garbage"},
    )
    assert resp.status_code == 401


# ---------------------------------------------------------------------------
# Refresh token
# ---------------------------------------------------------------------------

def test_refresh_token(client):
    login = client.post(
        "/api/v1/auth/login",
        data={"username": "admin", "password": "admin123"},
    )
    assert login.status_code == 200
    refresh_token = login.json()["refresh_token"]

    resp = client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": refresh_token},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert "access_token" in body
    assert body["username"] == "admin"


def test_refresh_with_access_token_fails(client):
    """Using an access token as refresh token must be rejected."""
    login = client.post(
        "/api/v1/auth/login",
        data={"username": "admin", "password": "admin123"},
    )
    access_token = login.json()["access_token"]

    resp = client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": access_token},
    )
    assert resp.status_code == 401
