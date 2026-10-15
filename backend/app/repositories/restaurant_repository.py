from pathlib import Path
import json
from json import JSONDecodeError
from pydantic import TypeAdapter, ValidationError
import warnings
from backend.app.schemas.restaurant import Restaurant

restaurants_list_adapter = TypeAdapter(list[Restaurant])

class RestaurantRepository:
    def __init__(self, restaurants_file_path: Path) -> None:
        self.restaurants_file_path: Path = restaurants_file_path

    def __load_restaurants(self) -> list[Restaurant]: 
        if not self.restaurants_file_path.exists():
            warnings.warn(f"'{self.restaurants_file_path.absolute()}' does not exist. Defaulting to empty restaurants list.")
            return []

        with open(self.restaurants_file_path, "r", encoding="utf-8") as restaurants_file:
            try:
                return restaurants_list_adapter.validate_python(json.load(restaurants_file))
            except JSONDecodeError as e:
                raise JSONDecodeError(f"{self.restaurants_file_path.absolute()} is not JSON serializable.", e.doc, e.pos) from e
            except ValidationError as e:
                raise ValueError(f"{self.restaurants_file_path.absolute()} does not follow the correct list[Restaurant] schema. See backend/app/schemas/restaurant.py or visit https://www.schema.org/Restaurant for schema specifications.") from e

    def get_all_restaurants(self) -> list[Restaurant]:
        return self.__load_restaurants()

    def get_restaurant_by_id(self, restaurant_id: str) -> Restaurant | None:
        restaurants = self.get_all_restaurants()
        
        for restaurant in restaurants:
            if restaurant.id == restaurant_id:
                return restaurant
        return None