from datetime import timezone
from decimal import Decimal
import pytest
from pydantic import ValidationError
from backend.app.schemas.order import Order, OrderItem


def test_create_order_model():
    item = OrderItem(
        menuItemId="latte123",
        name="Latte",
        quantity=2,
        unitPrice=Decimal("5.50"),
        lineTotal=Decimal("11.00")
    )

    order = Order(
        customerId="customer123",
        restaurantId="restaurant123",
        cartId="cart123",
        items=[item],
        currency="CAD",
        subtotal=Decimal("11.00"),
        total=Decimal("11.00"),
        deliveryAddress="123 Test Street"
    )

    assert order.id
    assert order.status == "created"
    assert order.items[0].name == "Latte"
    assert order.items[0].quantity == 2
    assert order.total == Decimal("11.00")
    assert order.createdAt.utcoffset().total_seconds() == 0
    serialized = order.model_dump(mode="json")  # Confirm JSON serialization succeeds
    assert serialized["id"] == order.id
    assert serialized["items"][0]["unitPrice"] == "5.50"


def test_order_item_rejects_invalid_quantity():
    with pytest.raises(ValidationError):
        OrderItem(
            menuItemId="latte123",
            name="Latte",
            quantity=-1,
            unitPrice=Decimal("5.50"),
            lineTotal=Decimal("0.00")
        )


def test_order_requires_items():
    with pytest.raises(ValidationError):
        Order(
            customerId="customer123",
            restaurantId="restaurant123",
            cartId="cart123",
            items=[],
            currency="CAD",
            subtotal=Decimal("0.00"),
            total=Decimal("0.00"),
            deliveryAddress="123 Test Street"
        )