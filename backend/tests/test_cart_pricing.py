from decimal import Decimal
import pytest
from backend.app.schemas.item_availability import ItemAvailability
from backend.app.services.cart_pricing import CartPricingError, price_cart


def test_cart_and_checkout_use_same_prices(checkout_setup):
    service, customer, cart_repo, _, _, _ = checkout_setup

    cart = cart_repo.get_active_cart(customer.id)
    menu_items = service.restaurant_service.menu_items_by_id()

    cart_result = price_cart(cart, menu_items, strict=False,)

    checkout_result = price_cart(cart, menu_items, strict=True,)

    assert cart_result.total == Decimal("10.98")
    assert checkout_result.total == cart_result.total


def test_strict_pricing_rejects_unavailable_item(checkout_setup,):
    service, customer, cart_repo, _, restaurant_repo, _ = checkout_setup

    restaurants = restaurant_repo.get_all_restaurants()
    item = restaurants[0].hasMenu.hasMenuSection[0].hasMenuItem[0]

    from backend.app.schemas.item_availability import ItemAvailability

    item.offers.availability = ItemAvailability.OUT_OF_STOCK
    restaurant_repo.save_restaurants(restaurants)

    cart = cart_repo.get_active_cart(customer.id)
    menu_items = service.restaurant_service.menu_items_by_id()

    display = price_cart(cart, menu_items, strict=False)
    assert display.items[0].available is False
    assert display.total == Decimal("0.00")

    with pytest.raises(CartPricingError):
        price_cart(cart, menu_items, strict=True)