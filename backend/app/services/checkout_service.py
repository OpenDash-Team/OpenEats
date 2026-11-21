from decimal import Decimal
from ..core.exceptions import CheckoutValidationError, CheckoutPermissionError
from ..repositories.cart_repository import CartRepository
from ..repositories.order_repository import OrderRepository
from ..services.restaurant_service import RestaurantService
from ..services.cart_service import round_money
from ..schemas.cart import MAX_QUANTITY
from ..schemas.customer import Customer
from ..schemas.item_availability import ItemAvailability
from ..schemas.order import Order, OrderItem

class CheckoutService:
    def __init__(
        self,
        cart_repository: CartRepository,
        order_repository: OrderRepository,
        restaurant_service: RestaurantService,
    ) -> None:
        self.cart_repository = cart_repository
        self.order_repository = order_repository
        self.restaurant_service = restaurant_service

    def checkout(self, customer: Customer) -> Order:

        # validate the customer
        if not customer.isActive:
            raise CheckoutPermissionError("Deactivated customers cannot check out")

        if customer.role != "customer":
            raise CheckoutPermissionError("Only customer accounts can check out")

        if not customer.address or not customer.address.strip():
            raise CheckoutValidationError("A delivery address is required for checkout")

        with self.cart_repository.lock(): # lock the cart during the checkout operation.
            carts = self.cart_repository.get_all_carts()
            cart = self.cart_repository.find_active_cart(carts, customer.id,)
            
            if cart is None:
                raise CheckoutValidationError("No active cart found")

            # lock orders while checking and saving
            with self.order_repository.lock():
                # Recovery if an earlier attempt saved the order but failed to close the cart
                existing_order = (self.order_repository.get_order_by_cart_id(cart.id))

                if existing_order is not None:
                    cart.status = "checkedOut"
                    self.cart_repository.save_carts(carts)
                    return existing_order

                # validate the cart
                if not cart.items:
                    raise CheckoutValidationError("Cannot check out an empty cart")

                if not cart.restaurantId:
                    raise CheckoutValidationError("Cart has no restaurant")

                restaurant = (self.restaurant_service.get_restaurant_by_id(cart.restaurantId))

                if restaurant is None:
                    raise CheckoutValidationError("Restaurant no longer exists")

                menu_items = (self.restaurant_service.menu_items_by_id())

                order_items = []
                subtotal = Decimal("0.00")
                currency = None

                # validate and reprice every item
                for cart_item in cart.items:

                    if not 1 <= cart_item.quantity <= MAX_QUANTITY:
                        raise CheckoutValidationError("Invalid item quantity")

                    result = menu_items.get(cart_item.menuItemId)

                    if result is None:
                        raise CheckoutValidationError(f"Menu item '{cart_item.menuItemId}' no longer exists")

                    restaurant_id, menu_item = result

                    if restaurant_id != cart.restaurantId:
                        raise CheckoutValidationError("Cart contains an item from another restaurant")

                    offers = (menu_item.offers if isinstance(menu_item.offers, list)else [menu_item.offers])

                    offer = next((o for o in offers if o.availability == ItemAvailability.IN_STOCK), None)

                    if offer is None:
                        raise CheckoutValidationError(f"'{menu_item.name}' is unavailable")

                    # one currency per order
                    if currency is None:
                        currency = offer.priceCurrency
                    elif currency != offer.priceCurrency:
                        raise CheckoutValidationError("Items have different currencies")

                    unit_price = offer.price
                    line_total = round_money(unit_price * cart_item.quantity)

                    subtotal += line_total

                    order_items.append(
                        OrderItem(
                            menuItemId=menu_item.id,
                            name=menu_item.name,
                            quantity=cart_item.quantity,
                            unitPrice=unit_price,
                            lineTotal=line_total,
                        )
                    )

                subtotal = round_money(subtotal)
                total = subtotal

                new_order = Order(
                    customerId=customer.id,
                    restaurantId=cart.restaurantId,
                    cartId=cart.id,
                    items=order_items,
                    currency=currency,
                    subtotal=subtotal,
                    total=total,
                    deliveryAddress=customer.address,
                )

                # persist the order first
                orders = self.order_repository.get_all_orders()
                orders.append(new_order)

                self.order_repository.save_orders(orders)

                # only lose the cart only after successful
                cart.status = "checkedOut"
                self.cart_repository.save_carts(carts)
                return new_order
            