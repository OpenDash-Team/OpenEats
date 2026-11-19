from decimal import Decimal

import threading

import pytest

from backend.app.core.exceptions import (
    CartItemNotFoundError,
    CartQuantityError,
    CustomerDeactivatedError,
    DifferentRestaurantError,
    MenuItemNotFoundError,
    MenuItemUnavailableError,
)
from backend.app.repositories.cart_repository import CartRepository
from backend.app.repositories.restaurant_repository import RestaurantRepository
from backend.app.schemas.cart import Cart
from backend.app.schemas.cart_request import CartItemAdd, CartItemUpdate
from backend.app.schemas.customer import Customer
from backend.app.schemas.item_availability import ItemAvailability
from backend.app.schemas.menu import Menu
from backend.app.schemas.menu_item import MenuItem
from backend.app.schemas.menu_section import MenuSection
from backend.app.schemas.offer import Offer
from backend.app.schemas.restaurant import Restaurant
from backend.app.services.cart_service import CartService
from backend.app.services.restaurant_service import RestaurantService

IN_STOCK = ItemAvailability.IN_STOCK
OUT_OF_STOCK = ItemAvailability.OUT_OF_STOCK


def menu_item(item_id, price, availability=IN_STOCK):
    return MenuItem(id=item_id, name=item_id.title(), suitableForDiet=[], offers=Offer(price=price, priceCurrency="CAD", availability=availability))


def restaurant(restaurant_id, *items):
    return Restaurant(
        id=restaurant_id, name=restaurant_id, address="1 Main St", telephone="+1-250-555-0100", openingHours="Mo-Su 09:00-21:00",
        hasMenu=Menu(hasMenuSection=[MenuSection(id="main", name="Main", hasMenuItem=list(items))]),
    )


@pytest.fixture
def restaurants(tmp_path):
    # Burger Place (burger, fries, shake out of stock) and Taco Place
    repository = RestaurantRepository(tmp_path / "restaurants.json")
    repository.save_restaurants([
        restaurant("burger-place", menu_item("burger", "10.00"), menu_item("fries", "3.50"), menu_item("shake", "4.00", OUT_OF_STOCK)),
        restaurant("taco-place", menu_item("taco", "4.25")),
    ])
    return repository


@pytest.fixture
def carts(tmp_path):
    repository = CartRepository(tmp_path / "carts.json")
    repository.save_carts([])
    return repository


@pytest.fixture
def service(restaurants, carts):
    return CartService(carts, RestaurantService(restaurants))


@pytest.fixture
def alex():
    return Customer(id="alex", name="Alex", email="alex@example.com", hashedPassword="hash")


def change_menu_item(restaurants, item_id, availability=None, price=None):
    all_restaurants = restaurants.get_all_restaurants()
    for r in all_restaurants:
        for item in r.hasMenu.hasMenuSection[0].hasMenuItem:
            if item.id == item_id:
                if availability:
                    item.offers.availability = availability
                if price:
                    item.offers.price = Decimal(price)
    restaurants.save_restaurants(all_restaurants)


# create or retrieve

def test_get_cart_creates_an_empty_cart(service, alex):
    cart = service.get_cart(alex)

    assert cart.customerId == "alex"
    assert cart.items == []
    assert cart.subtotal == Decimal("0.00")
    assert cart.total == Decimal("0.00")


def test_customer_only_ever_has_one_active_cart(service, carts, alex):
    first = service.get_cart(alex)
    second = service.get_cart(alex)

    assert first.id == second.id
    assert len(carts.get_all_carts()) == 1


def test_checked_out_cart_is_not_reused(service, carts, alex):
    carts.save_carts([Cart(id="old", customerId="alex", status="checkedOut")])

    cart = service.get_cart(alex)

    assert cart.id != "old"


# add

def test_add_items_and_backend_calculates_totals(service, alex):
    service.add_item(alex, CartItemAdd(menuItemId="burger", quantity=2))
    cart = service.add_item(alex, CartItemAdd(menuItemId="fries", quantity=3))

    assert [(i.menuItemId, i.lineTotal) for i in cart.items] == [("burger", Decimal("20.00")), ("fries", Decimal("10.50"))]
    assert cart.subtotal == Decimal("30.50")
    assert cart.total == Decimal("30.50")
    assert cart.currency == "CAD"
    assert cart.restaurantId == "burger-place"


def test_adding_same_item_again_increases_quantity(service, alex):
    service.add_item(alex, CartItemAdd(menuItemId="burger"))
    cart = service.add_item(alex, CartItemAdd(menuItemId="burger", quantity=2))

    assert len(cart.items) == 1
    assert cart.items[0].quantity == 3


def test_add_unknown_menu_item_raises(service, alex):
    with pytest.raises(MenuItemNotFoundError):
        service.add_item(alex, CartItemAdd(menuItemId="pizza"))


def test_add_out_of_stock_item_raises(service, alex):
    with pytest.raises(MenuItemUnavailableError):
        service.add_item(alex, CartItemAdd(menuItemId="shake"))


def test_add_item_from_second_restaurant_raises(service, alex):
    service.add_item(alex, CartItemAdd(menuItemId="burger"))

    with pytest.raises(DifferentRestaurantError):
        service.add_item(alex, CartItemAdd(menuItemId="taco"))


def test_adding_past_99_of_one_item_raises(service, alex):
    service.add_item(alex, CartItemAdd(menuItemId="burger", quantity=99))

    with pytest.raises(CartQuantityError):
        service.add_item(alex, CartItemAdd(menuItemId="burger"))


# update quantity

def test_update_quantity_recalculates_totals(service, alex):
    service.add_item(alex, CartItemAdd(menuItemId="burger"))

    cart = service.update_item_quantity(alex, "burger", CartItemUpdate(quantity=4))

    assert cart.items[0].quantity == 4
    assert cart.subtotal == Decimal("40.00")


def test_update_item_not_in_cart_raises(service, alex):
    with pytest.raises(CartItemNotFoundError):
        service.update_item_quantity(alex, "burger", CartItemUpdate(quantity=2))


# remove and clear

def test_remove_item(service, alex):
    service.add_item(alex, CartItemAdd(menuItemId="burger"))
    service.add_item(alex, CartItemAdd(menuItemId="fries"))

    cart = service.remove_item(alex, "burger")

    assert [i.menuItemId for i in cart.items] == ["fries"]
    assert cart.subtotal == Decimal("3.50")


def test_removing_last_item_lets_customer_order_from_another_restaurant(service, alex):
    service.add_item(alex, CartItemAdd(menuItemId="burger"))

    assert service.remove_item(alex, "burger").restaurantId is None
    assert service.add_item(alex, CartItemAdd(menuItemId="taco")).restaurantId == "taco-place"


def test_remove_item_not_in_cart_raises(service, alex):
    with pytest.raises(CartItemNotFoundError):
        service.remove_item(alex, "burger")


def test_clear_cart_empties_it_and_keeps_the_same_cart(service, alex):
    before = service.add_item(alex, CartItemAdd(menuItemId="burger", quantity=2))

    cart = service.clear_cart(alex)

    assert cart.id == before.id
    assert cart.items == []
    assert cart.restaurantId is None
    assert cart.total == Decimal("0.00")


# live prices

def test_cart_uses_current_menu_price(service, restaurants, alex):
    service.add_item(alex, CartItemAdd(menuItemId="burger", quantity=2))
    change_menu_item(restaurants, "burger", price="12.00")

    cart = service.get_cart(alex)

    assert cart.items[0].unitPrice == Decimal("12.00")
    assert cart.total == Decimal("24.00")


def test_item_that_went_out_of_stock_is_flagged_and_not_counted(service, restaurants, alex):
    service.add_item(alex, CartItemAdd(menuItemId="burger"))
    service.add_item(alex, CartItemAdd(menuItemId="fries"))
    change_menu_item(restaurants, "burger", availability=OUT_OF_STOCK)

    cart = service.get_cart(alex)

    burger = next(i for i in cart.items if i.menuItemId == "burger")
    assert burger.available is False
    assert burger.lineTotal == Decimal("0")
    assert cart.subtotal == Decimal("3.50")


def test_out_of_stock_item_can_be_removed_but_not_increased(service, restaurants, alex):
    service.add_item(alex, CartItemAdd(menuItemId="burger"))
    change_menu_item(restaurants, "burger", availability=OUT_OF_STOCK)

    with pytest.raises(MenuItemUnavailableError):
        service.update_item_quantity(alex, "burger", CartItemUpdate(quantity=2))

    assert service.remove_item(alex, "burger").items == []


def test_lowering_quantity_of_out_of_stock_item_is_allowed(service, restaurants, alex):
    service.add_item(alex, CartItemAdd(menuItemId="burger", quantity=3))
    change_menu_item(restaurants, "burger", availability=OUT_OF_STOCK)

    cart = service.update_item_quantity(alex, "burger", CartItemUpdate(quantity=1))

    assert cart.items[0].quantity == 1


def test_item_deleted_from_menu_is_flagged_and_can_be_removed(service, restaurants, alex):
    service.add_item(alex, CartItemAdd(menuItemId="burger"))
    service.add_item(alex, CartItemAdd(menuItemId="fries"))

    all_restaurants = restaurants.get_all_restaurants()
    section = all_restaurants[0].hasMenu.hasMenuSection[0]
    section.hasMenuItem = [item for item in section.hasMenuItem if item.id != "burger"]
    restaurants.save_restaurants(all_restaurants)

    cart = service.get_cart(alex)
    burger = next(i for i in cart.items if i.menuItemId == "burger")
    assert burger.name is None
    assert burger.available is False
    assert cart.subtotal == Decimal("3.50")

    with pytest.raises(MenuItemNotFoundError):
        service.update_item_quantity(alex, "burger", CartItemUpdate(quantity=2))

    assert [i.menuItemId for i in service.remove_item(alex, "burger").items] == ["fries"]


def test_money_is_rounded_half_up_to_cents(restaurants, carts, alex):
    restaurants.save_restaurants([restaurant("candy-shop", menu_item("candy", "0.125"))])
    service = CartService(carts, RestaurantService(restaurants))

    cart = service.add_item(alex, CartItemAdd(menuItemId="candy"))

    assert cart.items[0].lineTotal == Decimal("0.13")
    assert cart.total == Decimal("0.13")


# customers (multi-subsystem rule)

@pytest.mark.parametrize("action", [
    lambda s, c: s.get_cart(c),
    lambda s, c: s.add_item(c, CartItemAdd(menuItemId="burger")),
    lambda s, c: s.update_item_quantity(c, "burger", CartItemUpdate(quantity=2)),
    lambda s, c: s.remove_item(c, "burger"),
    lambda s, c: s.clear_cart(c),
])
def test_deactivated_customer_cannot_create_or_change_a_cart(service, carts, action):
    deactivated = Customer(id="sam", name="Sam", email="sam@example.com", hashedPassword="hash", isActive=False)

    with pytest.raises(CustomerDeactivatedError):
        action(service, deactivated)

    assert carts.get_all_carts() == []


def test_cart_is_still_there_after_restart(restaurants, carts, alex):
    CartService(carts, RestaurantService(restaurants)).add_item(alex, CartItemAdd(menuItemId="burger", quantity=2))

    # New repositories and service read the files again, like after a restart
    restarted = CartService(CartRepository(carts.file_path), RestaurantService(RestaurantRepository(restaurants.file_path)))
    cart = restarted.get_cart(alex)

    assert cart.items[0].quantity == 2
    assert cart.total == Decimal("20.00")


def test_parallel_adds_are_all_kept(restaurants, carts, alex):
    def add_one():
        # A new service per call, like separate requests
        CartService(CartRepository(carts.file_path), RestaurantService(restaurants)).add_item(alex, CartItemAdd(menuItemId="fries"))

    threads = [threading.Thread(target=add_one) for _ in range(10)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    assert carts.get_all_carts()[0].items[0].quantity == 10
