def test_create_menu_item_endpoint(client):
    response = client.post(
        "/restaurants/NwYJoaOHusWdiqXpM7mQH/menu-items",
        json={
            "name": "Test Mocha",
            "description": "Chocolate and espresso",
            "suitableForDiet": [
                "https://schema.org/VegetarianDiet"
            ],
            "offers": {
                "price": 4.99,
                "priceCurrency": "USD",
                "availability": "https://schema.org/InStock"
            }
        }
    )

    assert response.status_code == 201

    data = response.json()

    assert data["name"] == "Test Mocha"
    assert data["description"] == "Chocolate and espresso"
    assert data["id"] is not None

def test_create_menu_item_endpoint_invalid_restaurant(client):
    response = client.post(
        "/restaurants/not-a-real-id/menu-items",
        json={
            "name": "Test Mocha",
            "description": "Chocolate and espresso",
            "suitableForDiet": [
                "https://schema.org/VegetarianDiet"
            ],
            "offers": {
                "price": 4.99,
                "priceCurrency": "USD",
                "availability": "https://schema.org/InStock"
            }
        }
    )

    assert response.status_code == 404

    data = response.json()

    assert "not found" in data["detail"].lower()

# def test_create_menu_item_endpoint_invalid_section(client):
#     response = client.post(
#         "/restaurants/NwYJoaOHusWdiqXpM7mQH/menu-items",
#         json={
#             "name": "Test Mocha",
#             "description": "Chocolate and espresso",
#             "suitableForDiet": [
#                 "https://schema.org/VegetarianDiet"
#             ],
#             "offers": {
#                 "price": 4.99,
#                 "priceCurrency": "USD",
#                 "availability": "https://schema.org/InStock"
#             }
#         }
#     )

    # assert response.status_code == 422


def test_create_menu_item_endpoint_invalid_body(client):
    response = client.post(
        "/restaurants/NwYJoaOHusWdiqXpM7mQH/menu-items",
        json={"description": "Missing required fields"})

    assert response.status_code == 422

def test_update_menu_item_endpoint(client):
    response = client.patch(
        "/restaurants/NwYJoaOHusWdiqXpM7mQH/menu-sections/q9th4Uh9iO6lHbCEJIVz2/items/F5hn9s3VD9qzKsLV4z8CW",
        json={"description": "Updated through API"})

    assert response.status_code == 200
    data = response.json()
    assert data["description"] == "Updated through API"

def test_delete_menu_item_endpoint(client):
    response = client.delete("/restaurants/NwYJoaOHusWdiqXpM7mQH/menu-sections/q9th4Uh9iO6lHbCEJIVz2/items/F5hn9s3VD9qzKsLV4z8CW")
    assert response.status_code == 204

def test_delete_menu_item_endpoint_invalid_item(client):
    response = client.delete("/restaurants/NwYJoaOHusWdiqXpM7mQH/menu-sections/q9th4Uh9iO6lHbCEJIVz2/items/not-a-real-item")
    assert response.status_code == 404

def test_delete_menu_item_endpoint_invalid_restaurant(client):
    response = client.delete("/restaurants/not-a-real-restaurant/menu-sections/q9th4Uh9iO6lHbCEJIVz2/items/F5hn9s3VD9qzKsLV4z8CW")
    assert response.status_code == 404

def test_delete_menu_item_endpoint_invalid_section(client):
    response = client.delete("/restaurants/NwYJoaOHusWdiqXpM7mQH/menu-sections/not-a-real-section/items/F5hn9s3VD9qzKsLV4z8CW")
    assert response.status_code == 404


def test_create_menu_item_rejects_extra_fields(client):
    response = client.post("/restaurants/NwYJoaOHusWdiqXpM7mQH/menu-items",
        json={
            "name": "Test Lemon Tea",
            "description": "Test item",
            "suitableForDiet": [
                "https://schema.org/VegetarianDiet"
            ],
            "offers": {
                "price": 9.99,
                "priceCurrency": "USD",
                "availability": "https://schema.org/InStock"
            },
            "randomField": "this should not be allowed"
        }
    )

    assert response.status_code == 422


def test_create_menu_item_strips_whitespace(client):
    response = client.post("/restaurants/NwYJoaOHusWdiqXpM7mQH/menu-items",
        json={
            "name": "   Test Lemon Tea   ",
            "description": "   Lemon and Tea   ",
            "suitableForDiet": [
                "https://schema.org/VegetarianDiet"
            ],
            "offers": {
                "price": 9.99,
                "priceCurrency": "USD",
                "availability": "https://schema.org/InStock"
            }
        }
    )

    assert response.status_code == 201

    data = response.json()

    assert data["name"] == "Test Lemon Tea"
    assert data["description"] == "Lemon and Tea"


def test_update_menu_item_rejects_empty_body(client):
    response = client.patch("/restaurants/NwYJoaOHusWdiqXpM7mQH/menu-sections/q9th4Uh9iO6lHbCEJIVz2/items/F5hn9s3VD9qzKsLV4z8CW",
        json={}
    )

    assert response.status_code == 422