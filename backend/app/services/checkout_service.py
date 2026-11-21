from ..core.exceptions import CheckoutValidationError, CheckoutPermissionError
from ..repositories.cart_repository import CartRepository
from ..repositories.order_repository import OrderRepository
from ..services.restaurant_service import RestaurantService
from ..schemas.customer import Customer
from ..schemas.order import Order, OrderItem
from .cart_pricing import CartPricingError, price_cart

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


                menu_items = self.restaurant_service.menu_items_by_id() # retrieve current menu information

                # now it calculates prices using the same implementation as CartService
                try:
                    priced_cart = price_cart(cart, menu_items, strict=True,)
                except CartPricingError as e:
                    raise CheckoutValidationError(str(e)) from e

                order_items = []

                for item in priced_cart.items:
                    order_items.append(OrderItem(menuItemId=item.menuItemId, name=item.name, quantity=item.quantity, unitPrice=item.unitPrice, lineTotal=item.lineTotal))

                subtotal = priced_cart.subtotal
                total = priced_cart.total
                currency = priced_cart.currency

                assert currency is not None

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
            