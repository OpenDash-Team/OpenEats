from ..core.exceptions import CheckoutValidationError, CheckoutPermissionError
from ..repositories.cart_repository import CartRepository
from ..repositories.order_repository import OrderRepository
from ..services.cart_service import CartService
from ..services.restaurant_service import RestaurantService
from ..schemas.customer import Customer
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
        # prices come from the same code the cart uses, so checkout and cart totals can't differ
        self.cart_service = CartService(cart_repository, restaurant_service)

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
            cart = next((c for c in carts if c.customerId == customer.id and c.status == "active"), None)

            if cart is None:
                raise CheckoutValidationError("No active cart found")

            # lock orders while checking and saving
            with self.order_repository.lock():
                # Recovery if an earlier attempt saved the order but failed to close the cart
                existing_order = self.order_repository.get_order_by_cart_id(cart.id)

                if existing_order is not None:
                    cart.status = "checkedOut"
                    self.cart_repository.save_carts(carts)
                    return existing_order

                if not cart.items:
                    raise CheckoutValidationError("Cannot check out an empty cart")

                # revalidate availability and prices with the current menu
                priced_cart = self.cart_service.price_cart(cart, self.restaurant_service.menu_items_by_id())

                for item in priced_cart.items:
                    if item.name is None:
                        raise CheckoutValidationError(f"Menu item '{item.menuItemId}' no longer exists")
                    if not item.available:
                        raise CheckoutValidationError(f"'{item.name}' is unavailable")

                new_order = Order(
                    customerId=customer.id,
                    restaurantId=cart.restaurantId,
                    cartId=cart.id,
                    items=[
                        OrderItem(menuItemId=item.menuItemId, name=item.name, quantity=item.quantity, unitPrice=item.unitPrice, lineTotal=item.lineTotal)
                        for item in priced_cart.items
                    ],
                    currency=priced_cart.currency,
                    subtotal=priced_cart.subtotal,
                    total=priced_cart.total,
                    deliveryAddress=customer.address,
                )

                # persist the order first
                orders = self.order_repository.get_all_orders()
                orders.append(new_order)
                self.order_repository.save_orders(orders)

                # close the cart only after the order is saved
                cart.status = "checkedOut"
                self.cart_repository.save_carts(carts)
                return new_order
