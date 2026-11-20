import pytest

from fastapi.testclient import TestClient
from backend.app.main import main

ACTIVE_CUSTOMER_ID = "cust000000000000active"


def new_restaurant(**changes):
    data = {
        "name": "Taco Town",
        "address": "789 Pine St",
        "telephone": "+1-250-555-0300",
        "openingHours": "Mo-Sa 09:00-21:00",
    }
    return {**data, **changes}

# POST /restaurants

def test_create_restaurant_returns_201_with_new_restaurant(owner_client):
    response = owner_client.post("/api/v1/restaurants", json=new_restaurant())

    assert response.status_code == 201
    data = response.json()
    assert data["id"]
    assert data["name"] == "Taco Town"
    assert data["hasMenu"] is None

def test_created_restaurant_is_saved(owner_client):
    created = owner_client.post("/api/v1/restaurants", json=new_restaurant()).json()

    # A fresh app reads from the JSON file again, like after a restart
    restarted_client = TestClient(main())
    response = restarted_client.get(f"/api/v1/restaurants/{created['id']}")

    assert response.status_code == 200
    assert response.json()["name"] == "Taco Town"

def test_create_restaurant_with_missing_field_returns_422(owner_client):
    data = new_restaurant()
    del data["address"]

    response = owner_client.post("/api/v1/restaurants", json=data)

    assert response.status_code == 422

def test_create_restaurant_with_id_returns_422(owner_client):
    response = owner_client.post("/api/v1/restaurants", json=new_restaurant(id="my-own-id"))

    assert response.status_code == 422

def test_create_duplicate_restaurant_returns_409(owner_client):
    existing = owner_client.get("/api/v1/restaurants").json()[0]

    response = owner_client.post("/api/v1/restaurants", json=new_restaurant(name=existing["name"], address=existing["address"]))

    assert response.status_code == 409

# PATCH /restaurants/{restaurant_id}

def test_update_restaurant_changes_only_fields_sent(owner_client):
    existing = owner_client.get("/api/v1/restaurants").json()[0]

    response = owner_client.patch(f"/api/v1/restaurants/{existing['id']}", json={"telephone": "+1-250-555-0199"})

    assert response.status_code == 200
    data = response.json()
    assert data["telephone"] == "+1-250-555-0199"
    assert data["name"] == existing["name"]
    assert data["hasMenu"] == existing["hasMenu"]

def test_updated_restaurant_is_saved(owner_client):
    existing = owner_client.get("/api/v1/restaurants").json()[0]
    owner_client.patch(f"/api/v1/restaurants/{existing['id']}", json={"name": "Renamed Cafe"})

    restarted_client = TestClient(main())
    response = restarted_client.get(f"/api/v1/restaurants/{existing['id']}")

    assert response.json()["name"] == "Renamed Cafe"

def test_update_unknown_restaurant_returns_404(owner_client):
    response = owner_client.patch("/api/v1/restaurants/does-not-exist", json={"name": "New Name"})

    assert response.status_code == 404

def test_update_with_no_fields_returns_422(owner_client):
    existing = owner_client.get("/api/v1/restaurants").json()[0]

    response = owner_client.patch(f"/api/v1/restaurants/{existing['id']}", json={})

    assert response.status_code == 422

def test_update_with_invalid_opening_hours_returns_422(owner_client):
    existing = owner_client.get("/api/v1/restaurants").json()[0]

    response = owner_client.patch(f"/api/v1/restaurants/{existing['id']}", json={"openingHours": "always open"})

    assert response.status_code == 422

def test_update_into_duplicate_returns_409(owner_client):
    first, second = owner_client.get("/api/v1/restaurants").json()[:2]

    response = owner_client.patch(f"/api/v1/restaurants/{first['id']}", json={"name": second["name"], "address": second["address"]})

    assert response.status_code == 409


@pytest.mark.parametrize(
    "method,path,body",
    [
        ("post", "/api/v1/restaurants", new_restaurant()),
        ("patch", "/api/v1/restaurants/NwYJoaOHusWdiqXpM7mQH", {"telephone": "+1-250-555-0199"}),
        (
            "post",
            "/api/v1/restaurants/NwYJoaOHusWdiqXpM7mQH/menu-items",
            {
                "name": "Test Mocha",
                "description": "Chocolate and espresso",
                "suitableForDiet": ["https://schema.org/VegetarianDiet"],
                "offers": {
                    "price": 4.99,
                    "priceCurrency": "USD",
                    "availability": "https://schema.org/InStock",
                },
            },
        ),
        (
            "patch",
            "/api/v1/restaurants/NwYJoaOHusWdiqXpM7mQH/menu-items/F5hn9s3VD9qzKsLV4z8CW",
            {"description": "Owner update"},
        ),
        (
            "delete",
            "/api/v1/restaurants/NwYJoaOHusWdiqXpM7mQH/menu-items/F5hn9s3VD9qzKsLV4z8CW",
            None,
        ),
    ],
)
@pytest.mark.parametrize(
    "user_type,expected_status",
    [("anonymous", 401), ("customer", 403)],
)
def test_restaurant_and_menu_edits_require_owner(
    client,
    sign_in_as,
    method,
    path,
    body,
    user_type,
    expected_status,
):
    request_client = client if user_type == "anonymous" else sign_in_as(ACTIVE_CUSTOMER_ID)

    response = request_client.request(method, path, json=body)

    assert response.status_code == expected_status
