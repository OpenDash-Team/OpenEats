from pathlib import Path
from .json_repository import JsonRepository
from ..schemas.order import Order


class OrderRepository(JsonRepository[Order]):

    def __init__(self, orders_file_path: Path) -> None:
        super().__init__(orders_file_path, Order)

    def get_all_orders(self) -> list[Order]:
        return self._load_all()

    def save_orders(self, orders: list[Order]) -> None:
        self._save_all(orders)

    def get_order_by_id(self, order_id: str) -> Order | None:
        orders = self.get_all_orders()

        for order in orders:
            if order.id == order_id:
                return order
        return None

    def get_orders_by_customer(self, customer_id: str) -> list[Order]:
        orders = self.get_all_orders()
        return [order for order in orders if order.customerId == customer_id]

    def get_order_by_cart_id(self, cart_id: str) -> Order | None:
        orders = self.get_all_orders()
        for order in orders:
            if order.cartId == cart_id:
                return order
        return None