from decimal import Decimal
import pytest
from backend.app.core.exceptions import CheckoutValidationError, CheckoutPermissionError
from backend.app.repositories.cart_repository import CartRepository
from backend.app.repositories.order_repository import OrderRepository
from backend.app.repositories.restaurant_repository import RestaurantRepository
from backend.app.services.checkout_service import CheckoutService
from backend.app.services.restaurant_service import RestaurantService
from backend.app.schemas.customer import Customer
from backend.app.schemas.cart import Cart, CartItem
from backend.app.schemas.restaurant import Restaurant
from backend.app.schemas.menu import Menu
from backend.app.schemas.menu_section import MenuSection
from backend.app.schemas.menu_item import MenuItem
from backend.app.schemas.offer import Offer
from backend.app.schemas.item_availability import ItemAvailability
from backend.app.schemas.restricted_diet import RestrictedDiet


def test_successful_checkout(checkout_setup):
    (service, customer, cart_repo,order_repo, _, _,) = checkout_setup
    order = service.checkout(customer)
    assert order.customerId == customer.id
    assert order.total == Decimal("10.98")
    assert order.status == "created"
    assert len(order.items) == 1
    assert order.items[0].quantity == 2
    assert order.items[0].unitPrice == Decimal("5.49")
    saved_orders = order_repo.get_all_orders()
    assert len(saved_orders) == 1
    assert saved_orders[0].id == order.id
    carts = cart_repo.get_all_carts() # verify old cart is checked out
    assert carts[0].status == "checkedOut"


def test_checkout_rejects_unavailable_item(checkout_setup):
    (service, customer, cart_repo, order_repo, restaurant_repo, _,) = checkout_setup
    restaurants = restaurant_repo.get_all_restaurants()
    menu_item = (restaurants[0].hasMenu.hasMenuSection[0].hasMenuItem[0])
    menu_item.offers.availability = (ItemAvailability.OUT_OF_STOCK)
    restaurant_repo.save_restaurants(restaurants)

    with pytest.raises(CheckoutValidationError):
        service.checkout(customer)

    assert order_repo.get_all_orders() == []
    carts = cart_repo.get_all_carts()
    assert carts[0].status == "active"
    assert len(carts[0].items) == 1


def test_checkout_keeps_cart_when_order_save_fails(checkout_setup, monkeypatch,):
    (service, customer, cart_repo, order_repo, _, _,) = checkout_setup

    def fail_save(_orders):
        raise OSError("Simulated disk failure")

    monkeypatch.setattr(order_repo, "save_orders", fail_save,)

    with pytest.raises(OSError):
        service.checkout(customer)

    carts = cart_repo.get_all_carts()
    assert carts[0].status == "active"
    assert len(carts[0].items) == 1
    assert order_repo.get_all_orders() == []


def test_checkout_uses_current_menu_price(checkout_setup):
    (service, customer, _, order_repo, restaurant_repo, _,) = checkout_setup
    restaurants = restaurant_repo.get_all_restaurants()
    menu_item = (restaurants[0].hasMenu.hasMenuSection[0].hasMenuItem[0])
    menu_item.offers.price = Decimal("6.49")
    restaurant_repo.save_restaurants(restaurants)
    order = service.checkout(customer)

    assert order.total == Decimal("12.98")
    assert order.items[0].unitPrice == Decimal("6.49")
    saved_order = order_repo.get_all_orders()[0]
    assert saved_order.total == Decimal("12.98")


def test_checkout_rejects_empty_cart(checkout_setup):
    service, customer, cart_repo, order_repo, _, _ = checkout_setup
    carts = cart_repo.get_all_carts()
    carts[0].items = []
    cart_repo.save_carts(carts)
    with pytest.raises(CheckoutValidationError):
        service.checkout(customer)
    assert order_repo.get_all_orders() == []
    assert cart_repo.get_all_carts()[0].status == "active"

def test_checkout_requires_delivery_address(checkout_setup):
    service, customer, _, order_repo, _, _ = checkout_setup
    customer.address = None
    with pytest.raises(CheckoutValidationError):
        service.checkout(customer)
    assert order_repo.get_all_orders() == []

def test_checkout_rejects_deactivated_customer(checkout_setup):
    service, customer, _, order_repo, _, _ = checkout_setup
    customer.isActive = False
    with pytest.raises(CheckoutPermissionError):
        service.checkout(customer)
    assert order_repo.get_all_orders() == []