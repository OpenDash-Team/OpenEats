import pytest

FRAPPUCCINO = "F5hn9s3VD9qzKsLV4z8CW"
DOLCE_LATTE = "qGevRkwnKESbOSAxDkH5V"
DUNKIN_LATTE = "AYdIdKXXtZvNCKVy7Z6a1"
PASSWORD = "password123"


def register_and_login(client, email, name):
    account = {"name": name, "email": email, "password": PASSWORD}
    registration = client.post("/api/v1/customers", json=account)
    assert registration.status_code == 201

    response = client.post(
        "/api/v1/login",
        json={"email": email, "password": PASSWORD},
    )
    assert response.status_code == 200
    token_data = response.json()
    assert token_data["token_type"] == "bearer"

    return registration.json(), {"Authorization": f"Bearer {token_data['access_token']}"}


def test_real_token_can_read_and_manage_cart(client):
    customer, headers = register_and_login(client, "cart-owner@example.com", "Cart Owner")

    empty_cart = client.get("/api/v1/cart", headers=headers)
    assert empty_cart.status_code == 200
    assert empty_cart.json()["customerId"] == customer["id"]
    assert empty_cart.json()["items"] == []

    added = client.post(
        "/api/v1/cart/items",
        headers=headers,
        json={"menuItemId": FRAPPUCCINO, "quantity": 1},
    )
    assert added.status_code == 200
    assert added.json()["customerId"] == customer["id"]
    assert added.json()["items"][0]["menuItemId"] == FRAPPUCCINO

    updated = client.patch(
        f"/api/v1/cart/items/{FRAPPUCCINO}",
        headers=headers,
        json={"quantity": 2},
    )
    assert updated.status_code == 200
    assert updated.json()["items"][0]["quantity"] == 2

    removed = client.delete(f"/api/v1/cart/items/{FRAPPUCCINO}", headers=headers)
    assert removed.status_code == 200
    assert removed.json()["items"] == []

    client.post(
        "/api/v1/cart/items",
        headers=headers,
        json={"menuItemId": DOLCE_LATTE, "quantity": 1},
    )
    cleared = client.delete("/api/v1/cart", headers=headers)
    assert cleared.status_code == 200
    assert cleared.json()["customerId"] == customer["id"]
    assert cleared.json()["items"] == []


def test_real_tokens_keep_customers_carts_isolated(client):
    first_customer, first_headers = register_and_login(
        client,
        "first-cart-owner@example.com",
        "First Cart Owner",
    )
    second_customer, second_headers = register_and_login(
        client,
        "second-cart-owner@example.com",
        "Second Cart Owner",
    )

    first_add = client.post(
        "/api/v1/cart/items",
        headers=first_headers,
        json={"menuItemId": FRAPPUCCINO, "quantity": 1},
    )
    second_add = client.post(
        "/api/v1/cart/items",
        headers=second_headers,
        json={"menuItemId": DUNKIN_LATTE, "quantity": 2},
    )
    assert first_add.status_code == second_add.status_code == 200

    first_cart = client.get("/api/v1/cart", headers=first_headers).json()
    second_cart = client.get("/api/v1/cart", headers=second_headers).json()
    assert first_cart["customerId"] == first_customer["id"]
    assert second_cart["customerId"] == second_customer["id"]
    assert [item["menuItemId"] for item in first_cart["items"]] == [FRAPPUCCINO]
    assert [item["menuItemId"] for item in second_cart["items"]] == [DUNKIN_LATTE]

    assert client.delete("/api/v1/cart", headers=second_headers).status_code == 200
    first_cart_after_clear = client.get("/api/v1/cart", headers=first_headers).json()
    assert [item["menuItemId"] for item in first_cart_after_clear["items"]] == [FRAPPUCCINO]


def test_deactivated_users_token_cannot_access_customer_or_cart_routes(client):
    account, headers = register_and_login(
        client,
        "deactivated-cart-owner@example.com",
        "Deactivated Cart Owner",
    )
    add_response = client.post(
        "/api/v1/cart/items",
        headers=headers,
        json={"menuItemId": FRAPPUCCINO, "quantity": 1},
    )
    assert add_response.status_code == 200

    assert client.delete("/api/v1/customers/me", headers=headers).status_code == 204

    protected_requests = [
        ("get", "/api/v1/customers/me", None),
        ("patch", "/api/v1/customers/me", {"address": "1 Main St"}),
        ("delete", "/api/v1/customers/me", None),
        ("get", "/api/v1/cart", None),
        ("delete", "/api/v1/cart", None),
        ("post", "/api/v1/cart/items", {"menuItemId": FRAPPUCCINO, "quantity": 1}),
        ("patch", f"/api/v1/cart/items/{FRAPPUCCINO}", {"quantity": 1}),
        ("delete", f"/api/v1/cart/items/{FRAPPUCCINO}", None),
    ]
    for method, path, body in protected_requests:
        response = client.request(method, path, headers=headers, json=body)
        assert response.status_code == 401, f"{method.upper()} {path} returned {response.status_code}"

    login_response = client.post(
        "/api/v1/login",
        json={"email": account["email"], "password": PASSWORD},
    )
    assert login_response.status_code == 401
    assert "access_token" not in login_response.json()


@pytest.mark.parametrize("auth", ["missing", "invalid"])
def test_rejected_cart_mutations_leave_cart_unchanged(client, auth):
    customer, owner_headers = register_and_login(
        client,
        f"cart-owner-{auth}@example.com",
        "Cart Owner",
    )
    initial = client.post(
        "/api/v1/cart/items",
        headers=owner_headers,
        json={"menuItemId": FRAPPUCCINO, "quantity": 1},
    )
    assert initial.status_code == 200

    rejected_headers = {} if auth == "missing" else {"Authorization": "Bearer not-a-jwt"}
    mutations = [
        ("post", "/api/v1/cart/items", {"menuItemId": DOLCE_LATTE, "quantity": 1}),
        ("patch", f"/api/v1/cart/items/{FRAPPUCCINO}", {"quantity": 2}),
        ("delete", f"/api/v1/cart/items/{FRAPPUCCINO}", None),
        ("delete", "/api/v1/cart", None),
    ]
    for method, path, body in mutations:
        response = client.request(method, path, headers=rejected_headers, json=body)
        assert response.status_code == 401, f"{method.upper()} {path} returned {response.status_code}"

        cart = client.get("/api/v1/cart", headers=owner_headers)
        assert cart.status_code == 200
        assert cart.json()["customerId"] == customer["id"]
        assert [(item["menuItemId"], item["quantity"]) for item in cart.json()["items"]] == [
            (FRAPPUCCINO, 1),
        ]
