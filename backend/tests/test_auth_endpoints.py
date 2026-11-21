from datetime import datetime, timedelta, timezone

import jwt
import pytest

from backend.app.core.security import ALGORITHM, SECRET_KEY, create_access_token


PASSWORD = "password123"


def register_customer(client, email="auth@example.com", name="Auth Customer"):
    account = {"name": name, "email": email, "password": PASSWORD}
    response = client.post("/api/v1/customers", json=account)

    assert response.status_code == 201
    return account, response.json()


def token_for(client, email, password=PASSWORD):
    response = client.post("/api/v1/login", json={"email": email, "password": password})
    assert response.status_code == 200
    return response.json()


def make_invalid_token(kind):
    if kind == "malformed":
        return "not-a-jwt"
    if kind == "tampered":
        header, payload, _ = create_access_token({"sub": "unknown"}).split(".")
        return f"{header}.{payload}.invalidsignature"
    if kind == "expired":
        expired_at = datetime.now(timezone.utc) - timedelta(minutes=1)
        return jwt.encode(
            {"sub": "unknown", "exp": expired_at},
            SECRET_KEY,
            algorithm=ALGORITHM,
        )
    if kind == "missing-subject":
        return create_access_token({})
    if kind == "missing-version":
        return create_access_token({"sub": "unknown"})
    if kind == "boolean-version":
        return create_access_token({"sub": "unknown", "ver": True})
    if kind == "non-string-subject":
        return create_access_token({"sub": 123})
    if kind == "unknown-customer":
        return create_access_token({"sub": "missing-customer"})
    raise AssertionError(f"Unknown invalid-token case: {kind}")


def test_login_returns_bearer_token_for_valid_credentials(client):
    account, created = register_customer(client)

    response = client.post(
        "/api/v1/login",
        json={"email": account["email"], "password": account["password"]},
    )

    assert response.status_code == 200
    token_data = response.json()
    assert set(token_data) == {"access_token", "token_type"}
    assert token_data["access_token"]
    assert token_data["token_type"] == "bearer"
    assert "password" not in token_data
    assert "hashedPassword" not in token_data

    profile = client.get(
        "/api/v1/customers/me",
        headers={"Authorization": f"Bearer {token_data['access_token']}"},
    )
    assert profile.status_code == 200
    assert profile.json()["id"] == created["id"]


def test_login_accepts_email_with_different_case(client):
    account, _ = register_customer(client)

    response = client.post(
        "/api/v1/login",
        json={"email": account["email"].upper(), "password": account["password"]},
    )

    assert response.status_code == 200
    assert response.json()["token_type"] == "bearer"


def test_login_rejects_wrong_password(client):
    account, _ = register_customer(client)

    response = client.post(
        "/api/v1/login",
        json={"email": account["email"], "password": "incorrect123"},
    )

    assert response.status_code == 401
    assert "access_token" not in response.json()


def test_login_rejects_short_wrong_password(client):
    account, _ = register_customer(client)

    response = client.post(
        "/api/v1/login",
        json={"email": account["email"], "password": "short"},
    )

    assert response.status_code == 401
    assert "access_token" not in response.json()


def test_login_rejects_unknown_email(client):
    response = client.post(
        "/api/v1/login",
        json={"email": "missing@example.com", "password": PASSWORD},
    )

    assert response.status_code == 401
    assert "access_token" not in response.json()


def test_deactivated_customer_cannot_log_in_again(client):
    account, _ = register_customer(client)
    token_data = token_for(client, account["email"], account["password"])
    headers = {"Authorization": f"Bearer {token_data['access_token']}"}

    assert client.delete("/api/v1/customers/me", headers=headers).status_code == 204

    response = client.post(
        "/api/v1/login",
        json={"email": account["email"], "password": account["password"]},
    )
    assert response.status_code == 401
    assert "access_token" not in response.json()


@pytest.mark.parametrize(
    "method,path,body",
    [
        ("get", "/api/v1/customers/me", None),
        ("patch", "/api/v1/customers/me", {"address": "1 Main St"}),
        ("delete", "/api/v1/customers/me", None),
        ("get", "/api/v1/cart", None),
        ("delete", "/api/v1/cart", None),
        ("post", "/api/v1/cart/items", {"menuItemId": "F5hn9s3VD9qzKsLV4z8CW", "quantity": 1}),
        ("patch", "/api/v1/cart/items/F5hn9s3VD9qzKsLV4z8CW", {"quantity": 1}),
        ("delete", "/api/v1/cart/items/F5hn9s3VD9qzKsLV4z8CW", None),
    ],
)
@pytest.mark.parametrize(
    "token_kind",
    [
        "malformed",
        "tampered",
        "expired",
        "missing-subject",
        "missing-version",
        "boolean-version",
        "non-string-subject",
        "unknown-customer",
    ],
)
def test_protected_routes_reject_invalid_tokens(client, method, path, body, token_kind):
    token = make_invalid_token(token_kind)

    response = client.request(
        method,
        path,
        headers={"Authorization": f"Bearer {token}"},
        json=body,
    )

    assert response.status_code == 401


def test_logout_invalidates_old_tokens_but_allows_login_again(client):
    account, created = register_customer(client)
    first_login = token_for(client, account["email"], account["password"])
    old_headers = {"Authorization": f"Bearer {first_login['access_token']}"}

    logout = client.post("/api/v1/logout", headers=old_headers)
    assert logout.status_code == 200
    assert logout.json() == {"message": "Successfully logged out."}

    assert client.get("/api/v1/customers/me", headers=old_headers).status_code == 401

    second_login = token_for(client, account["email"], account["password"])
    new_headers = {"Authorization": f"Bearer {second_login['access_token']}"}
    assert client.get("/api/v1/customers/me", headers=new_headers).status_code == 200
    assert client.get("/api/v1/customers/me", headers=new_headers).json()["id"] == created["id"]

    second_logout = client.post("/api/v1/logout", headers=new_headers)
    assert second_logout.status_code == 200


def test_logout_requires_a_valid_token(client):
    response = client.post("/api/v1/logout")
    assert response.status_code == 401
    assert response.headers["www-authenticate"] == "Bearer"

    old_token = create_access_token({"sub": "missing-customer", "ver": 0})
    response = client.post(
        "/api/v1/logout",
        headers={"Authorization": f"Bearer {old_token}"},
    )
    assert response.status_code == 401
