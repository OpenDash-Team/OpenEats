from decimal import Decimal
import pytest
from fastapi.testclient import TestClient
from backend.app.main import main
from backend.app.core.dependencies import get_current_customer, get_checkout_service
from backend.app.core.exceptions import CheckoutPermissionError, CheckoutValidationError
from backend.app.schemas.customer import Customer
from backend.app.schemas.order import Order, OrderItems

@pytest.fixture
def customer():
    return Customer(
        name="Test Customer",
        email="checkout@example.com",
        hashedPassword="dummy-test-hash",
        address="123 Test Street",
        role="customer",
        isActive=True,
    )

@pytest.fixture
def test_app():
    app = main()
    yield app
    app.dependency_overrides.clear()


def make_test_order(customer: Customer) -> Order:
    return Order(
        customerId=customer.id,
        restaurantId="restaurant123",
        cartId="cart123",
        items=[
            OrderItem(
                menuItemId="latte123",
                name="Latte",
                quantity=2,
                unitPrice=Decimal("5.49"),
                lineTotal=Decimal("10.98"),
            )
        ],
        currency="CAD",
        subtotal=Decimal("10.98"),
        total=Decimal("10.98"),
        deliveryAddress=customer.address,
    )

def test_checkout_endpoint_success(test_app, customer):
    expected_order = make_test_order(customer)
    class FakeCheckoutService:
        def checkout(self, current_customer):
            assert current_customer.id == customer.id
            return expected_order

    test_app.dependency_overrides[get_current_customer] = (lambda: customer)
    test_app.dependency_overrides[get_checkout_service] = (lambda: FakeCheckoutService())

    client = TestClient(test_app)
    response = client.post("/api/v1/checkout")
    assert response.status_code == 201
    data = response.json()
    assert data["id"] == expected_order.id
    assert data["customerId"] == customer.id
    assert Decimal(data["total"]) == Decimal("10.98")
    assert data["items"][0]["name"] == "Latte"


def test_checkout_requires_authentication(test_app):
    test_app.dependency_overrides[get_current_customer] = (lambda: None)
    client = TestClient(test_app)
    response = client.post("/api/v1/checkout")
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"


def test_checkout_invalid_cart(test_app, customer):
    class FakeCheckoutService:
        def checkout(self, current_customer):
            raise CheckoutValidationError("Cannot check out an empty cart")

    test_app.dependency_overrides[get_current_customer] = (lambda: customer)
    test_app.dependency_overrides[get_checkout_service] = (lambda: FakeCheckoutService())

    client = TestClient(test_app)
    response = client.post("/api/v1/checkout")
    assert response.status_code == 409
    assert "empty cart" in response.json()["detail"]

def test_checkout_rejects_owner_role(test_app, customer):
    customer.role = "owner"
    class FakeCheckoutService:
        def checkout(self, current_customer):
            raise CheckoutPermissionError("Only customer accounts can check out")

    test_app.dependency_overrides[get_current_customer] = (lambda: customer)
    test_app.dependency_overrides[get_checkout_service] = (lambda: FakeCheckoutService())
    client = TestClient(test_app)
    response = client.post("/api/v1/checkout")
    assert response.status_code == 403

def test_checkout_end_to_end(checkout_setup):
    (service, customer, cart_repo, order_repo, _, _,) = checkout_setup
    app = main()
    app.dependency_overrides[get_current_customer] = (lambda: customer)
    app.dependency_overrides[get_checkout_service] = (lambda: service)

    try:
        with TestClient(app) as client:
            response = client.post("/api/v1/checkout")

        assert response.status_code == 201
        data = response.json()
        assert data["customerId"] == customer.id
        assert data["total"] == "10.98"
        orders = order_repo.get_all_orders()
        carts = cart_repo.get_all_carts()
        assert len(orders) == 1
        assert orders[0].id == data["id"]
        assert orders[0].total == Decimal("10.98")
        assert carts[0].status == "checkedOut"

    finally:
        app.dependency_overrides.clear()