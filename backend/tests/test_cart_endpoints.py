import pytest

ALEX = "cust000000000000active"  # active customer in test-data/customers.json

# Items in test-data/restaurants.json
STARBUCKS = "NwYJoaOHusWdiqXpM7mQH"
FRAPPUCCINO = "F5hn9s3VD9qzKsLV4z8CW"  # Starbucks, 5.95
DOLCE_LATTE = "qGevRkwnKESbOSAxDkH5V"  # Starbucks, 5.65
DUNKIN_LATTE = "AYdIdKXXtZvNCKVy7Z6a1"  # Dunkin, 5.49


@pytest.fixture
def alex(sign_in_as):
    return sign_in_as(ALEX)


def add(client, menu_item_id, quantity=1):
    return client.post("/api/v1/cart/items", json={"menuItemId": menu_item_id, "quantity": quantity})


# Not signed in

@pytest.mark.parametrize("method, path", [
    ("get", "/api/v1/cart"),
    ("delete", "/api/v1/cart"),
    ("post", "/api/v1/cart/items"),
    ("patch", f"/api/v1/cart/items/{FRAPPUCCINO}"),
    ("delete", f"/api/v1/cart/items/{FRAPPUCCINO}"),
])
def test_cart_endpoints_need_sign_in(client, method, path):
    if method == "post":
        body = {"menuItemId": FRAPPUCCINO, "quantity": 1}
    elif method == "patch":
        body = {"quantity": 1}
    else:
        body = None

    response = client.request(method, path, json=body)

    assert response.status_code == 401


# GET /cart

def test_get_cart_creates_empty_cart(alex):
    response = alex.get("/api/v1/cart")

    assert response.status_code == 200
    data = response.json()
    assert data["customerId"] == ALEX
    assert data["items"] == []
    assert data["subtotal"] == "0.00"
    assert data["total"] == "0.00"


# POST /cart/items

def test_add_items_returns_cart_with_backend_totals(alex):
    add(alex, FRAPPUCCINO, 2)
    response = add(alex, DOLCE_LATTE)

    assert response.status_code == 200
    data = response.json()
    assert data["restaurantId"] == STARBUCKS
    assert [(i["menuItemId"], i["quantity"], i["lineTotal"]) for i in data["items"]] == [(FRAPPUCCINO, 2, "11.90"), (DOLCE_LATTE, 1, "5.65")]
    assert data["subtotal"] == "17.55"
    assert data["total"] == "17.55"
    assert data["currency"] == "USD"


def test_client_cannot_send_its_own_price(alex):
    response = alex.post("/api/v1/cart/items", json={"menuItemId": FRAPPUCCINO, "quantity": 1, "unitPrice": "0.01"})

    assert response.status_code == 422


def test_add_unknown_item_returns_404(alex):
    assert add(alex, "does-not-exist").status_code == 404


def test_add_item_from_second_restaurant_returns_409(alex):
    add(alex, FRAPPUCCINO)

    response = add(alex, DUNKIN_LATTE)

    assert response.status_code == 409


@pytest.mark.parametrize("quantity", [0, 100, "2", True])
def test_add_with_invalid_quantity_returns_422(alex, quantity):
    assert add(alex, FRAPPUCCINO, quantity).status_code == 422


def test_adding_past_99_returns_409(alex):
    add(alex, FRAPPUCCINO, 99)

    assert add(alex, FRAPPUCCINO).status_code == 409


# PATCH /cart/items/{id}

def test_update_quantity(alex):
    add(alex, FRAPPUCCINO)

    response = alex.patch(f"/api/v1/cart/items/{FRAPPUCCINO}", json={"quantity": 3})

    assert response.status_code == 200
    assert response.json()["items"][0]["quantity"] == 3
    assert response.json()["total"] == "17.85"


@pytest.mark.parametrize("quantity", [0, 100])
def test_update_with_invalid_quantity_returns_422(alex, quantity):
    add(alex, FRAPPUCCINO)

    assert alex.patch(f"/api/v1/cart/items/{FRAPPUCCINO}", json={"quantity": quantity}).status_code == 422


def test_update_item_not_in_cart_returns_404(alex):
    assert alex.patch(f"/api/v1/cart/items/{FRAPPUCCINO}", json={"quantity": 3}).status_code == 404


# DELETE /cart/items/{id} and DELETE /cart

def test_remove_item(alex):
    add(alex, FRAPPUCCINO)
    add(alex, DOLCE_LATTE)

    response = alex.delete(f"/api/v1/cart/items/{FRAPPUCCINO}")

    assert response.status_code == 200
    assert [i["menuItemId"] for i in response.json()["items"]] == [DOLCE_LATTE]
    assert response.json()["total"] == "5.65"


def test_remove_item_not_in_cart_returns_404(alex):
    assert alex.delete(f"/api/v1/cart/items/{FRAPPUCCINO}").status_code == 404


def test_clear_cart_then_order_from_another_restaurant(alex):
    add(alex, FRAPPUCCINO)

    cleared = alex.delete("/api/v1/cart")

    assert cleared.status_code == 200
    assert cleared.json()["items"] == []
    assert add(alex, DUNKIN_LATTE).status_code == 200


def test_each_customer_has_their_own_cart(client, alex, sign_in_as):
    add(alex, FRAPPUCCINO, 2)
    jordan_id = client.post("/api/v1/customers", json={"name": "Jordan", "email": "jordan@example.com", "password": "password123"}).json()["id"]
    jordan = sign_in_as(jordan_id)

    add(jordan, DUNKIN_LATTE)

    assert [i["menuItemId"] for i in alex.get("/api/v1/cart").json()["items"]] == [FRAPPUCCINO]
    assert [i["menuItemId"] for i in jordan.get("/api/v1/cart").json()["items"]] == [DUNKIN_LATTE]


# Multi-subsystem: customers + restaurants + cart

def test_deactivated_customer_cannot_use_a_cart(alex):
    add(alex, FRAPPUCCINO)

    alex.delete("/api/v1/customers/me")

    assert alex.get("/api/v1/cart").status_code == 401
    assert add(alex, DOLCE_LATTE).status_code == 401


def test_item_marked_out_of_stock_by_restaurant_is_flagged_in_cart(client, alex):
    add(alex, FRAPPUCCINO)
    add(alex, DOLCE_LATTE)

    # The restaurant marks the frappuccino out of stock through the menu item endpoint
    response = client.patch(
        f"/api/v1/restaurants/{STARBUCKS}/menu-items/{FRAPPUCCINO}",
        json={"offers": {"price": 5.95, "priceCurrency": "USD", "availability": "https://schema.org/OutOfStock"}},
    )
    assert response.status_code == 200

    cart = alex.get("/api/v1/cart").json()
    frappuccino = next(i for i in cart["items"] if i["menuItemId"] == FRAPPUCCINO)
    assert frappuccino["available"] is False
    assert cart["total"] == "5.65"
    assert add(alex, FRAPPUCCINO).status_code == 409


def test_raising_quantity_of_out_of_stock_item_returns_409(client, alex):
    add(alex, FRAPPUCCINO)
    client.patch(
        f"/api/v1/restaurants/{STARBUCKS}/menu-items/{FRAPPUCCINO}",
        json={"offers": {"price": 5.95, "priceCurrency": "USD", "availability": "https://schema.org/OutOfStock"}},
    )

    assert alex.patch(f"/api/v1/cart/items/{FRAPPUCCINO}", json={"quantity": 2}).status_code == 409
