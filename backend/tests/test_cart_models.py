import pytest
from pydantic import ValidationError

from backend.app.schemas.cart import Cart
from backend.app.schemas.cart_request import CartItemAdd


def test_new_cart_is_active_and_empty():
    cart = Cart(customerId="c1")

    assert cart.status == "active"
    assert cart.items == []
    assert cart.restaurantId is None


def test_add_defaults_to_quantity_one():
    assert CartItemAdd(menuItemId="item1").quantity == 1


@pytest.mark.parametrize("quantity", [0, -1, 100, "2", True, 1.5])
def test_add_rejects_invalid_quantity(quantity):
    with pytest.raises(ValidationError):
        CartItemAdd(menuItemId="item1", quantity=quantity)


def test_add_rejects_empty_menu_item_id():
    with pytest.raises(ValidationError):
        CartItemAdd(menuItemId="  ")
