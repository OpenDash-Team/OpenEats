from pathlib import Path

from .json_repository import JsonRepository
from ..schemas.customer import Customer


class CustomerRepository(JsonRepository[Customer]):
    def __init__(self, customers_file_path: Path) -> None:
        super().__init__(customers_file_path, Customer)

    def get_all_customers(self) -> list[Customer]:
        return self._load_all()

    def save_customers(self, customers: list[Customer]) -> None:
        self._save_all(customers)

    def get_customer_by_id(self, customer_id: str) -> Customer | None:
        for customer in self.get_all_customers():
            if customer.id == customer_id:
                return customer
        return None

    def get_customer_by_email(self, email: str) -> Customer | None:
        for customer in self.get_all_customers():
            if customer.email == email.lower():
                return customer
        return None
