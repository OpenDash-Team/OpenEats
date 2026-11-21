from decimal import Decimal
from ..schemas.cart import Cart, CartItemResponse, CartResponse
from ..schemas.item_availability import ItemAvailability
from ..schemas.menu_item import MenuItem
from ..schemas.offer import Offer
from .cart_service import round_money
from .money import round_money

class CartPricingError(Exception):
    """A cart cannot be priced for checkout."""


def find_in_stock_offer(menu_item: MenuItem) -> Offer | None:
    offers = (menu_item.offers if isinstance(menu_item.offers, list) else [menu_item.offers])

    return next((offer for offer in offers if offer is not None and offer.availability == ItemAvailability.IN_STOCK), None,)

def price_cart(cart: Cart, menu_items: dict[str, tuple[str, MenuItem]], strict: bool = False,) -> CartResponse:

    response_items: list[CartItemResponse] = []
    subtotal = Decimal("0.00")
    currency: str | None = None

    for cart_item in cart.items:
        result = menu_items.get(cart_item.menuItemId)

        if result is None:
            if strict:
                raise CartPricingError(f"Menu item '{cart_item.menuItemId}' no longer exists")

            menu_item = None
            offer = None

        else:
            restaurant_id, menu_item = result

            if (strict and restaurant_id != cart.restaurantId):
                raise CartPricingError("Cart contains an item from another restaurant")

            offer = find_in_stock_offer(menu_item)

        if offer is None:
            if strict:
                raise CartPricingError(f"Menu item '{cart_item.menuItemId}' is unavailable")

            line_total = Decimal("0.00")
        else:
            if currency is None:
                currency = offer.priceCurrency

            elif (strict and currency != offer.priceCurrency):
                raise CartPricingError("Items have different currencies")

            line_total = round_money(offer.price * cart_item.quantity)
            subtotal += line_total

        response_items.append(
            CartItemResponse(
                menuItemId=cart_item.menuItemId,
                name=(
                    menu_item.name
                    if menu_item is not None
                    else None
                ),
                quantity=cart_item.quantity,
                unitPrice=(
                    offer.price
                    if offer is not None
                    else None
                ),
                lineTotal=line_total,
                available=offer is not None,
            )
        )

    subtotal = round_money(subtotal)

    return CartResponse(
        id=cart.id,
        customerId=cart.customerId,
        restaurantId=cart.restaurantId,
        items=response_items,
        currency=currency,
        subtotal=subtotal,
        total=subtotal,
    )
