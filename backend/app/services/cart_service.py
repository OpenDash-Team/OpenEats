from decimal import ROUND_HALF_UP, Decimal

from ..core.exceptions import (
    CartItemNotFoundError,
    CartQuantityError,
    CustomerDeactivatedError,
    DifferentRestaurantError,
    MenuItemNotFoundError,
    MenuItemUnavailableError,
)
from ..repositories.cart_repository import CartRepository
from ..schemas.cart import MAX_QUANTITY, Cart, CartItem, CartItemResponse, CartResponse
from ..schemas.cart_request import CartItemAdd, CartItemUpdate
from ..schemas.customer import Customer
from ..schemas.item_availability import ItemAvailability
from ..schemas.menu_item import MenuItem
from ..schemas.offer import Offer
from .restaurant_service import RestaurantService


def round_money(amount: Decimal) -> Decimal:
    # Normal rounding to cents (0.125 -> 0.13), Decimal rounds half to even by default
    return amount.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


class CartService:
    def __init__(self, cart_repository: CartRepository, restaurant_service: RestaurantService):
        self.repository: CartRepository = cart_repository
        self.restaurant_service: RestaurantService = restaurant_service

    def get_cart(self, customer: Customer) -> CartResponse:
        """Returns the customer's active cart, creating an empty one if they don't have one yet."""
        self._check_customer_active(customer)

        with self.repository.lock():
            carts = self.repository.get_all_carts()
            cart = self._find_active_cart(carts, customer.id)

            if cart is None:
                cart = Cart(customerId=customer.id)
                carts.append(cart)
                self.repository.save_carts(carts)

        return self._to_response(cart, self.restaurant_service.menu_items_by_id())

    def add_item(self, customer: Customer, request: CartItemAdd) -> CartResponse:
        self._check_customer_active(customer)

        menu_items = self.restaurant_service.menu_items_by_id()
        restaurant_id, menu_item = self._find_orderable_menu_item(menu_items, request.menuItemId)

        with self.repository.lock():
            carts = self.repository.get_all_carts()
            cart = self._find_or_create_active_cart(carts, customer.id)

            if cart.items and cart.restaurantId != restaurant_id:
                raise DifferentRestaurantError("Your cart has items from another restaurant. Clear it first to order from this one")

            cart_item = next((item for item in cart.items if item.menuItemId == menu_item.id), None)

            if cart_item is None:
                cart.items.append(CartItem(menuItemId=menu_item.id, quantity=request.quantity))
            elif cart_item.quantity + request.quantity > MAX_QUANTITY:
                raise CartQuantityError(f"You can have at most {MAX_QUANTITY} of one item in your cart")
            else:
                cart_item.quantity += request.quantity

            cart.restaurantId = restaurant_id
            self.repository.save_carts(carts)

        return self._to_response(cart, menu_items)

    def update_item_quantity(self, customer: Customer, menu_item_id: str, request: CartItemUpdate) -> CartResponse:
        self._check_customer_active(customer)

        menu_items = self.restaurant_service.menu_items_by_id()

        with self.repository.lock():
            carts = self.repository.get_all_carts()
            cart, cart_item = self._find_cart_item(carts, customer.id, menu_item_id)

            # Ordering more needs the item to still be available, going down is always fine
            if request.quantity > cart_item.quantity:
                self._find_orderable_menu_item(menu_items, menu_item_id)

            cart_item.quantity = request.quantity
            self.repository.save_carts(carts)

        return self._to_response(cart, menu_items)

    def remove_item(self, customer: Customer, menu_item_id: str) -> CartResponse:
        # Works even if the item went out of stock or was deleted from the menu
        self._check_customer_active(customer)

        with self.repository.lock():
            carts = self.repository.get_all_carts()
            cart, cart_item = self._find_cart_item(carts, customer.id, menu_item_id)

            cart.items.remove(cart_item)
            if not cart.items:
                cart.restaurantId = None  # an empty cart can be used for any restaurant again

            self.repository.save_carts(carts)

        return self._to_response(cart, self.restaurant_service.menu_items_by_id())

    def clear_cart(self, customer: Customer) -> CartResponse:
        self._check_customer_active(customer)

        with self.repository.lock():
            carts = self.repository.get_all_carts()
            cart = self._find_or_create_active_cart(carts, customer.id)

            cart.items = []
            cart.restaurantId = None
            self.repository.save_carts(carts)

        return self._to_response(cart, {})  # empty cart, nothing to price

    def _to_response(self, cart: Cart, menu_items: dict[str, tuple[str, MenuItem]]) -> CartResponse:
        """Prices the cart with current menu prices. Items that can't be ordered are shown but not counted."""
        response_items = []
        subtotal = Decimal("0.00")
        currency = None

        for cart_item in cart.items:
            _, menu_item = menu_items.get(cart_item.menuItemId, (None, None))
            offer = self._in_stock_offer(menu_item) if menu_item is not None else None

            if offer is None:
                line_total = Decimal("0.00")
            else:
                line_total = round_money(offer.price * cart_item.quantity)
                subtotal += line_total
                currency = offer.priceCurrency

            response_items.append(CartItemResponse(
                menuItemId=cart_item.menuItemId,
                name=menu_item.name if menu_item is not None else None,
                quantity=cart_item.quantity,
                unitPrice=offer.price if offer is not None else None,
                lineTotal=line_total,
                available=offer is not None,
            ))

        return CartResponse(
            id=cart.id,
            customerId=cart.customerId,
            restaurantId=cart.restaurantId,
            items=response_items,
            currency=currency,
            subtotal=subtotal,
            total=subtotal,  # no fees or tax yet
        )

    def _check_customer_active(self, customer: Customer) -> None:
        if not customer.isActive:
            raise CustomerDeactivatedError(f"Customer with id '{customer.id}' is deactivated")

    def _find_active_cart(self, carts: list[Cart], customer_id: str,) -> Cart | None:
        return self.repository.find_active_cart(carts, customer_id,)

    def _find_or_create_active_cart(self, carts: list[Cart], customer_id: str) -> Cart:
        cart = self._find_active_cart(carts, customer_id)

        if cart is None:
            cart = Cart(customerId=customer_id)
            carts.append(cart)

        return cart

    def _find_cart_item(self, carts: list[Cart], customer_id: str, menu_item_id: str) -> tuple[Cart, CartItem]:
        cart = self._find_active_cart(carts, customer_id)
        cart_item = next((item for item in cart.items if item.menuItemId == menu_item_id), None) if cart else None

        if cart_item is None:
            raise CartItemNotFoundError(f"Menu item with id '{menu_item_id}' is not in your cart")

        return cart, cart_item

    def _find_orderable_menu_item(self, menu_items: dict[str, tuple[str, MenuItem]], menu_item_id: str) -> tuple[str, MenuItem]:
        if menu_item_id not in menu_items:
            raise MenuItemNotFoundError(f"Menu item with id '{menu_item_id}' is not found")

        restaurant_id, menu_item = menu_items[menu_item_id]
        if self._in_stock_offer(menu_item) is None:
            raise MenuItemUnavailableError(f"'{menu_item.name}' is not available right now")

        return restaurant_id, menu_item

    def _in_stock_offer(self, menu_item: MenuItem) -> Offer | None:
        # An item can have one offer or a list, the first one in stock sets the price
        offers = menu_item.offers if isinstance(menu_item.offers, list) else [menu_item.offers]
        return next((offer for offer in offers if offer.availability == ItemAvailability.IN_STOCK), None)
