from backend.app.repositories.cart_repository import CartRepository
from backend.app.repositories.order_repository import OrderRepository
from backend.app.services.restaurant_service import RestaurantService


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