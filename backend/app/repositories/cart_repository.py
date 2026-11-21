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
        carts = self.get_all_carts()
        return self.find_active_cart(carts, customer_id)


    @staticmethod
    def find_active_cart(carts: list[Cart], customer_id: str,) -> Cart | None:
        return next((cart for cart in carts if cart.customerId == customer_id and cart.status == "active"), None,)

