import pytest
from pydantic import ValidationError

from backend.app.schemas.cart import Cart
from backend.app.schemas.cart_request import CartItemAdd, CartItemUpdate


def test_new_cart_is_active_and_empty():
    cart = Cart(customerId="c1")

    assert cart.status == "active"
    assert cart.items == []
    assert cart.restaurantId is None


def test_add_defaults_to_quantity_one():
    assert CartItemAdd(menuItemId="item1").quantity == 1


@pytest.mark.parametrize("quantity", [0, -1, 100])
def test_add_rejects_quantity_outside_1_to_99(quantity):
    with pytest.raises(ValidationError):
        CartItemAdd(menuItemId="item1", quantity=quantity)


@pytest.mark.parametrize("quantity", [1, 99])
def test_update_accepts_quantity_limits(quantity):
    assert CartItemUpdate(quantity=quantity).quantity == quantity


def test_update_rejects_zero_quantity():
    with pytest.raises(ValidationError):
        CartItemUpdate(quantity=0)


def test_add_rejects_empty_menu_item_id():
    with pytest.raises(ValidationError):
        CartItemAdd(menuItemId="  ")


def test_add_rejects_fields_the_client_should_not_set():
    with pytest.raises(ValidationError):
        CartItemAdd(menuItemId="item1", price="0.01")
