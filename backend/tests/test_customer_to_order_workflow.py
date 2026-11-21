from decimal import Decimal

from fastapi.testclient import TestClient

from backend.app.main import main
from backend.app.repositories.order_repository import OrderRepository
from backend.tests.conftest import REAL_DATA

FRAPPUCCINO = "F5hn9s3VD9qzKsLV4z8CW"  # Starbucks item in test-data/restaurants.json, 5.95


def login(client, email):
    token = client.post("/api/v1/login", json={"email": email, "password": "password123"}).json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def set_frappuccino_price(client, owner, restaurant_id, price):
    offers = {"price": price, "priceCurrency": "USD", "availability": "https://schema.org/InStock"}
    response = client.patch(f"/api/v1/restaurants/{restaurant_id}/menu-items/{FRAPPUCCINO}", json={"offers": offers}, headers=owner)
    assert response.status_code == 200


def test_customer_to_order_workflow(client):
    # Customer: register and sign in
    registered = client.post("/api/v1/customers", json={
        "name": "Jordan Smith", "email": "jordan@example.com", "password": "password123", "address": "1 Main St, Kelowna",
    })
    assert registered.status_code == 201
    customer = login(client, "jordan@example.com")

    # Restaurant and menu: find the restaurant that sells the item
    restaurants = client.get("/api/v1/restaurants?name=Starbucks").json()
    restaurant_id = restaurants[0]["id"]
    assert client.get(f"/api/v1/restaurants/{restaurant_id}").status_code == 200

    # Cart: add the item, backend works out the total
    cart = client.post("/api/v1/cart/items", json={"menuItemId": FRAPPUCCINO, "quantity": 2}, headers=customer).json()
    assert cart["total"] == "11.90"

    # The owner changes the price before checkout, checkout has to use the new one
    owner = login(client, "owner@example.com")
    set_frappuccino_price(client, owner, restaurant_id, 6.50)

    # Checkout: creates the order and closes the cart
    response = client.post("/api/v1/checkout", headers=customer)
    assert response.status_code == 201
    order = response.json()
    assert order["customerId"] == registered.json()["id"]
    assert order["restaurantId"] == restaurant_id
    assert order["deliveryAddress"] == "1 Main St, Kelowna"
    assert order["items"][0]["unitPrice"] == "6.5"
    assert order["total"] == "13.00"
    assert client.get("/api/v1/cart", headers=customer).json()["items"] == []

    # Order: still there after a restart, and a later price change doesn't touch it
    set_frappuccino_price(client, owner, restaurant_id, 9.99)
    restarted = TestClient(main())
    login(restarted, "jordan@example.com")

    saved = OrderRepository(REAL_DATA / "orders.json").get_all_orders()
    assert [o.id for o in saved] == [order["id"]]
    assert saved[0].items[0].name.startswith("Caramel Ribbon Crunch")
    assert saved[0].items[0].unitPrice == Decimal("6.5")
    assert saved[0].total == Decimal("13.00")
