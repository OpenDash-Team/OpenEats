import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient

from backend.app.core.dependencies import get_current_customer, get_customer_service
from backend.app.core.exceptions import CustomerDeactivatedError, CustomerNotFoundError
from backend.app.main import main

ACTIVE_CUSTOMER_ID = "cust000000000000active"  # Alex Morgan in test-data/customers.json


def new_customer(**changes):
    data = {"name": "Jordan Smith", "email": "jordan@example.com", "password": "password123"}
    return {**data, **changes}


def client_signed_in_as(customer_id):
    # Login (JWT) is a separate task, so these tests pretend the request is signed in
    # by replacing get_current_customer, the same way the real one will look the customer up.
    def fake_current_customer():
        try:
            return get_customer_service().get_active_customer(customer_id)
        except (CustomerNotFoundError, CustomerDeactivatedError):
            raise HTTPException(status_code=401, detail="Not authenticated")

    app = main()
    app.dependency_overrides[get_current_customer] = fake_current_customer
    return TestClient(app)


@pytest.fixture
def signed_in_client():
    return client_signed_in_as(ACTIVE_CUSTOMER_ID)


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
    created = client.post("/api/v1/customers", json=new_customer()).json()

    # A fresh app reads customers.json again, like after a restart
    response = client_signed_in_as(created["id"]).get("/api/v1/customers/me")

    assert response.status_code == 200
    assert response.json()["name"] == "Jordan Smith"


def test_register_with_existing_email_returns_409(client):
    response = client.post("/api/v1/customers", json=new_customer(email="Alex@Example.com"))

    assert response.status_code == 409


def test_register_with_invalid_email_returns_422(client):
    response = client.post("/api/v1/customers", json=new_customer(email="nope"))

    assert response.status_code == 422


# Not signed in

@pytest.mark.parametrize("method", ["get", "patch", "delete"])
def test_my_account_endpoints_need_sign_in(client, method):
    kwargs = {"json": {"name": "Hacker"}} if method == "patch" else {}

    response = getattr(client, method)("/api/v1/customers/me", **kwargs)

    assert response.status_code == 401


# GET /customers/me

def test_get_my_info_returns_signed_in_customer(signed_in_client):
    response = signed_in_client.get("/api/v1/customers/me")

    assert response.status_code == 200
    assert response.json()["email"] == "alex@example.com"
    assert "hashedPassword" not in response.json()


# PATCH /customers/me

def test_update_delivery_address(signed_in_client):
    response = signed_in_client.patch("/api/v1/customers/me", json={"address": "999 New Rd, Kelowna, BC"})

    assert response.status_code == 200
    assert response.json()["address"] == "999 New Rd, Kelowna, BC"
    assert response.json()["name"] == "Alex Morgan"


def test_update_to_taken_email_returns_409(signed_in_client):
    signed_in_client.post("/api/v1/customers", json=new_customer())

    response = signed_in_client.patch("/api/v1/customers/me", json={"email": "jordan@example.com"})

    assert response.status_code == 409


def test_update_with_no_fields_returns_422(signed_in_client):
    response = signed_in_client.patch("/api/v1/customers/me", json={})

    assert response.status_code == 422


def test_update_cannot_change_role(signed_in_client):
    response = signed_in_client.patch("/api/v1/customers/me", json={"name": "Alex", "role": "admin"})

    assert response.status_code == 422
    assert signed_in_client.get("/api/v1/customers/me").json()["role"] == "customer"


# DELETE /customers/me

def test_deactivate_returns_204_and_locks_the_account(signed_in_client):
    response = signed_in_client.delete("/api/v1/customers/me")

    assert response.status_code == 204

    # The same customer can't use their account anymore
    assert signed_in_client.get("/api/v1/customers/me").status_code == 401
