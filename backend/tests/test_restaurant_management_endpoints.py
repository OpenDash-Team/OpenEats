from fastapi.testclient import TestClient
from backend.app.main import main

def new_restaurant(**changes):
    data = {
        "name": "Taco Town",
        "address": "789 Pine St",
        "telephone": "+1-250-555-0300",
        "openingHours": "Mo-Sa 09:00-21:00",
    }
    return {**data, **changes}

# POST /restaurants

def test_create_restaurant_returns_201_with_new_restaurant(client):
    response = client.post("/restaurants", json=new_restaurant())

    assert response.status_code == 201
    data = response.json()
    assert data["id"]
    assert data["name"] == "Taco Town"
    assert data["hasMenu"] is None

def test_created_restaurant_is_saved(client):
    created = client.post("/restaurants", json=new_restaurant()).json()

    # A fresh app reads from the JSON file again, like after a restart
    restarted_client = TestClient(main())
    response = restarted_client.get(f"/restaurants/{created['id']}")

    assert response.status_code == 200
    assert response.json()["name"] == "Taco Town"

def test_create_restaurant_with_missing_field_returns_422(client):
    data = new_restaurant()
    del data["address"]

    response = client.post("/restaurants", json=data)

    assert response.status_code == 422

def test_create_restaurant_with_id_returns_422(client):
    response = client.post("/restaurants", json=new_restaurant(id="my-own-id"))

    assert response.status_code == 422

def test_create_duplicate_restaurant_returns_409(client):
    existing = client.get("/restaurants").json()[0]

    response = client.post("/restaurants", json=new_restaurant(name=existing["name"], address=existing["address"]))

    assert response.status_code == 409
