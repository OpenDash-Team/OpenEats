from pathlib import Path

from ..services.restaurant_service import RestaurantService
from ..repositories.restaurant_repository import RestaurantRepository

def get_data_dir() -> Path:
    data_dir = Path(__file__).resolve().parents[2] / "data"
    if not data_dir.exists(): data_dir.mkdir()
    return data_dir

def get_restaurant_service():
    restaurant_repository = RestaurantRepository(get_data_dir() / "restaurants.json")
    return RestaurantService(restaurant_repository)