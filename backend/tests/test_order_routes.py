from decimal import Decimal

import pytest
from fastapi.testclient import TestClient

from backend.app.core.dependencies import get_current_customer, get_order_repository
from backend.app.main import main
from backend.app.schemas.customer import Customer
from backend.app.schemas.order import Order, OrderItem


def make_order(customer_id: str, order_id: str) -> Order:
    return Order(
        id=order_id,
        customerId=customer_id,
        restaurantId="restaurant123",
        cartId=f"cart-{order_id}",
        items=[
            OrderItem(
                menuItemId="latte123",
                name="Latte",
                quantity=1,
                unitPrice=Decimal("5.50"),
                lineTotal=Decimal("5.50"),
            )
        ],
        currency="CAD",
        subtotal=Decimal("5.50"),
        total=Decimal("5.50"),
        deliveryAddress="456 Test Street",
    )


class FakeOrderRepository:
    def __init__(self, orders: list[Order]):
        self.orders = orders

    def get_order_by_id(self, order_id: str) -> Order | None:
        return next((order for order in self.orders if order.id == order_id), None)

    def get_orders_by_customer(self, customer_id: str) -> list[Order]:
        return [order for order in self.orders if order.customerId == customer_id]


@pytest.fixture
def app():
    test_app = main()
    yield test_app
    test_app.dependency_overrides.clear()


def test_get_order_by_id_is_public_and_returns_404_for_missing_order(app):
    order = make_order("customer123", "order123")
    app.dependency_overrides[get_order_repository] = lambda: FakeOrderRepository([order])
    client = TestClient(app)

    response = client.get("/api/v1/orders/order123")
    missing_response = client.get("/api/v1/orders/missing")

    assert response.status_code == 200
    assert response.json()["id"] == "order123"
    assert missing_response.status_code == 404
    assert missing_response.json()["detail"] == "Order not found"


def test_get_orders_by_customer_id_is_public(app):
    order = make_order("customer123", "order123")
    app.dependency_overrides[get_order_repository] = lambda: FakeOrderRepository([order])

    response = TestClient(app).get("/api/v1/customers/customer123/orders")

    assert response.status_code == 200
    assert [item["id"] for item in response.json()] == ["order123"]


def test_get_my_orders_requires_authentication_and_only_returns_own_orders(app):
    orders = [
        make_order("customer123", "order123"),
        make_order("customer456", "order456"),
    ]
    app.dependency_overrides[get_order_repository] = lambda: FakeOrderRepository(orders)
    client = TestClient(app)

    unauthenticated_response = client.get("/api/v1/orders/me")
    app.dependency_overrides[get_current_customer] = lambda: Customer(
        name="Test Customer",
        email="customer@example.com",
        hashedPassword="test-hash",
        address="123 Test Street",
        role="customer",
        isActive=True,
        id="customer123",
    )
    authenticated_response = client.get("/api/v1/orders/me")

    assert unauthenticated_response.status_code == 401
    assert authenticated_response.status_code == 200
    assert [item["id"] for item in authenticated_response.json()] == ["order123"]
