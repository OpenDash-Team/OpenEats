from pathlib import Path

from .json_repository import JsonRepository
from ..schemas.cart import Cart


class CartRepository(JsonRepository[Cart]):
    def __init__(self, carts_file_path: Path) -> None:
        super().__init__(carts_file_path, Cart)

    def get_all_carts(self) -> list[Cart]:
        return self._load_all()

    def save_carts(self, carts: list[Cart]) -> None:
        self._save_all(carts)

    def get_active_cart(self, customer_id: str) -> Cart | None:
        for cart in self.get_all_carts():
            if cart.customerId == customer_id and cart.status == "active":
                return cart
        return None
