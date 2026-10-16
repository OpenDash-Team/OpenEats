import pytest
import json
from backend.app.repositories.restaurant_repository import RestaurantRepository

DUMMY_JSON = [
    {
        "type": "Restaurant",
        "id": "123",
        "name": "Burger Joint",
        "address": "123 Main St",
        "telephone": "555-0100",
        "openingHours": "Mo-Su 09:00-22:00",
        "hasMenu": None
    },
    {
        "type": "Restaurant",
        "id": "456",
        "name": "Pizza Place",
        "address": "456 Oak St",
        "telephone": "555-0200",
        "openingHours": "Mo-Su 11:00-23:00",
        "hasMenu": None
    }
]

@pytest.fixture
def test_repo(tmp_path):
    """Creates a temporary JSON file and initializes the repository with it."""
    file_path = tmp_path / "test_restaurants.json"
    file_path.write_text(json.dumps(DUMMY_JSON))
    return RestaurantRepository(restaurants_file_path=file_path)

def test_get_restaurant_by_id_success(test_repo):
    restaurant = test_repo.get_restaurant_by_id("456")
    
    assert restaurant is not None
    assert restaurant.id == "456"
    assert restaurant.name == "Pizza Place"

def test_get_restaurant_by_id_not_found(test_repo):
    restaurant = test_repo.get_restaurant_by_id("non-existent-id")
    
    assert restaurant is None