from pathlib import Path

from .json_repository import JsonRepository
from ..schemas.restaurant import Restaurant


class RestaurantRepository(JsonRepository[Restaurant]):
    def __init__(self, restaurants_file_path: Path) -> None:
        super().__init__(restaurants_file_path, Restaurant)

    def get_all_restaurants(self) -> list[Restaurant]:
        return self._load_all()

    def save_restaurants(self, restaurants: list[Restaurant]) -> None:
        self._save_all(restaurants)

    def get_restaurant_by_id(self, restaurant_id: str) -> Restaurant | None:
        for restaurant in self.get_all_restaurants():
            if restaurant.id == restaurant_id:
                return restaurant
        return None
