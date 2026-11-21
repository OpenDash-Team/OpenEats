import pytest

from backend.app.core.security import create_access_token
ACTIVE_CUSTOMER_ID = "cust000000000000active"  # Alex Morgan in test-data/customers.json


def new_customer(**changes):
    data = {"name": "Jordan Smith", "email": "jordan@example.com", "password": "password123"}
    return {**data, **changes}


def sign_in(client, customer):
    response = client.post(
        "/api/v1/login",
        json={"email": customer["email"], "password": customer["password"]},
    )

    assert response.status_code == 200
    access_token = response.json()["access_token"]
    client.headers["Authorization"] = f"Bearer {access_token}"
    return client


@pytest.fixture
def signed_in_client(client):
    account = new_customer()
    registration = client.post("/api/v1/customers", json=account)
    assert registration.status_code == 201
    return sign_in(client, account)


# POST /customers

def test_register_returns_201_without_password(client):
    response = client.post("/api/v1/customers", json=new_customer(address="1 Main St"))

    assert response.status_code == 201
    data = response.json()
    assert data["id"]
    assert data["email"] == "jordan@example.com"
    assert data["address"] == "1 Main St"
    assert data["role"] == "customer"
    assert data["isActive"] is True
    assert "password" not in data
    assert "hashedPassword" not in data


def test_registered_customer_is_saved(client):
    account = new_customer()
    created = client.post("/api/v1/customers", json=account).json()

    response = sign_in(client, account).get("/api/v1/customers/me")

    assert response.status_code == 200
    assert response.json()["id"] == created["id"]
    assert response.json()["name"] == account["name"]


def test_register_with_existing_email_returns_409(client):
    response = client.post("/api/v1/customers", json=new_customer(email="Alex@Example.com"))

    assert response.status_code == 409


def test_register_with_invalid_email_returns_422(client):
    response = client.post("/api/v1/customers", json=new_customer(email="nope"))

    assert response.status_code == 422


# Not signed in

@pytest.mark.parametrize("method", ["get", "patch", "delete"])
def test_my_account_endpoints_need_sign_in(client, method):
    body = {"name": "Hacker"} if method == "patch" else None

    response = client.request(method, "/api/v1/customers/me", json=body)

    assert response.status_code == 401


@pytest.mark.parametrize(
    "token",
    ["not-a-jwt", create_access_token({"sub": 123})],
)
def test_my_account_endpoints_reject_invalid_tokens(client, token):
    response = client.get(
        "/api/v1/customers/me",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 401


def test_my_account_endpoints_reject_tokens_for_unknown_customers(client):
    token = create_access_token({"sub": "missing-customer"})

    response = client.get(
        "/api/v1/customers/me",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 401


# GET /customers/me

def test_get_my_info_returns_signed_in_customer(signed_in_client):
    response = signed_in_client.get("/api/v1/customers/me")

    assert response.status_code == 200
    assert response.json()["email"] == "jordan@example.com"
    assert "hashedPassword" not in response.json()


# PATCH /customers/me

def test_update_delivery_address(signed_in_client):
    response = signed_in_client.patch("/api/v1/customers/me", json={"address": "999 New Rd, Kelowna, BC"})

    assert response.status_code == 200
    assert response.json()["address"] == "999 New Rd, Kelowna, BC"
    assert response.json()["name"] == "Jordan Smith"


def test_update_to_taken_email_returns_409(signed_in_client):
    signed_in_client.post("/api/v1/customers", json=new_customer(email="taken@example.com"))

    response = signed_in_client.patch("/api/v1/customers/me", json={"email": "taken@example.com"})

    assert response.status_code == 409


def test_update_with_no_fields_returns_422(signed_in_client):
    response = signed_in_client.patch("/api/v1/customers/me", json={})

    assert response.status_code == 422


def test_update_cannot_change_role(signed_in_client):
    response = signed_in_client.patch("/api/v1/customers/me", json={"name": "Alex", "role": "owner"})

    assert response.status_code == 422
    assert signed_in_client.get("/api/v1/customers/me").json()["role"] == "customer"


# DELETE /customers/me

def test_deactivate_returns_204_and_locks_the_account(signed_in_client):
    response = signed_in_client.delete("/api/v1/customers/me")

    assert response.status_code == 204

    # The same customer can't use their account anymore
    assert signed_in_client.get("/api/v1/customers/me").status_code == 401
