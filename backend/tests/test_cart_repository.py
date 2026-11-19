from backend.app.repositories.cart_repository import CartRepository
from backend.app.schemas.cart import Cart, CartItem


def test_get_active_cart_skips_checked_out_and_other_customers(tmp_path):
    repo = CartRepository(tmp_path / "carts.json")
    repo.save_carts([
        Cart(id="old", customerId="c1", status="checkedOut"),
        Cart(id="someone-else", customerId="c2"),
        Cart(id="mine", customerId="c1", items=[CartItem(menuItemId="m1", quantity=2)]),
    ])

    cart = repo.get_active_cart("c1")

    assert cart.id == "mine"
    assert cart.items[0].quantity == 2


def test_get_active_cart_returns_none_when_customer_has_none(tmp_path):
    repo = CartRepository(tmp_path / "carts.json")
    repo.save_carts([])

    assert repo.get_active_cart("c1") is None
