from decimal import Decimal
from backend.app.repositories.order_repository import OrderRepository
from backend.app.schemas.order import Order, OrderItem


def make_test_order(customer_id: str = "customer123", cart_id: str = "cart123") -> Order:
    return Order(
        customerId=customer_id,
        restaurantId="restaurant123",
        cartId=cart_id,
        items=[
            OrderItem(
                menuItemId="latte123",
                name="Latte",
                quantity=2,
                unitPrice=Decimal("5.50"),
                lineTotal=Decimal("11.00")
            )
        ],
        currency="CAD",
        subtotal=Decimal("11.00"),
        total=Decimal("11.00"),
        deliveryAddress="456 Test Street"
    )


def test_save_and_load_order(tmp_path):
    test_file = tmp_path / "orders.json"
    repository = OrderRepository(test_file)
    order = make_test_order()
    repository.save_orders([order])
    reloaded_repository = OrderRepository(test_file)
    loaded_orders = reloaded_repository.get_all_orders()

    assert len(loaded_orders) == 1
    loaded_order = loaded_orders[0]
    assert loaded_order.id == order.id
    assert loaded_order.customerId == "customer123"
    assert loaded_order.total == Decimal("11.00")
    assert loaded_order.items[0].name == "Latte"
    assert loaded_order.items[0].unitPrice == Decimal("5.50")


def test_get_orders_by_customer(tmp_path):
    repository = OrderRepository(tmp_path / "orders.json")
    order1 = make_test_order(customer_id="customerA",cart_id="cartA")
    order2 = make_test_order(customer_id="customerB", cart_id="cartB")
    order3 = make_test_order(customer_id="customerA",cart_id="cartC")

    repository.save_orders([order1, order2, order3])

    customer_orders = repository.get_orders_by_customer("customerA")
    assert len(customer_orders) == 2
    assert {order.id for order in customer_orders} == {order1.id,order3.id}


def test_get_order_by_cart_id(tmp_path):
    repository = OrderRepository(tmp_path / "orders.json")
    order = make_test_order()
    repository.save_orders([order])
    found_order = repository.get_order_by_cart_id("cart123")
    assert found_order is not None
    assert found_order.id == order.id
    assert repository.get_order_by_cart_id("nonexistent-cart") is None