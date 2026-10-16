from pathlib import Path
import json
from json import JSONDecodeError
from pydantic import TypeAdapter, ValidationError
import warnings
from backend.app.schemas.restaurant import Restaurant
import os
import tempfile

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

    def __save_restaurants(self, restaurants: list[Restaurant]) -> None:
        temp_file_path = None

        try:
            with tempfile.NamedTemporaryFile(mode = "w",
                                            encoding = "utf-8",
                                            dir = self.restaurants_file_path.parent, #creates temporary file in the same directory as the original JSON
                                            delete = False, # so python won't delete this file when the while bloack is exited
                                            suffix = ".tmp") as temp_file:
                temp_file_path = temp_file.name

                json.dump([restaurant.model_dump(mode="json") for restaurant in restaurants], temp_file, indent=4)

            os.replace(temp_file_path, self.restaurants_file_path)

        except OSError as e:
            if temp_file_path is not None:
                try:
                    os.remove(temp_file_path) # removes failed temp files so that they don't accumulate
                except FileNotFoundError:
                    pass

            raise OSError(f"Failed to save restaurants to '{self.restaurants_file_path.absolute()}'") from e

    def get_all_restaurants(self) -> list[Restaurant]:
        return self.__load_restaurants()

    def save_restaurants(self, restaurants: list[Restaurant]) -> None:
        self.__save_restaurants(restaurants)