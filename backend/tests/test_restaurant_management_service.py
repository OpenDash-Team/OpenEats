import pytest
from unittest.mock import Mock

from backend.app.core.exceptions import DuplicateRestaurantError
from backend.app.schemas.restaurant import Restaurant
from backend.app.schemas.restaurant_request import RestaurantCreate
from backend.app.services.restaurant_service import RestaurantService

@pytest.fixture
def existing_restaurants():
    return [
        Restaurant(id="1", name="Pizza Palace", address="123 Main St", telephone="+1-250-555-0100", openingHours="Mo-Su 11:00-22:00"),
        Restaurant(id="2", name="Burger Barn", address="456 Oak St", telephone="+1-250-555-0200", openingHours="Mo-Fr 10:00-20:00"),
    ]

@pytest.fixture
def repository(existing_restaurants):
    repository = Mock()
    repository.get_all_restaurants.return_value = existing_restaurants
    return repository

@pytest.fixture
def service(repository):
    return RestaurantService(repository)

def create_request(**changes):
    data = {
        "name": "Taco Town",
        "address": "789 Pine St",
        "telephone": "+1-250-555-0300",
        "openingHours": "Mo-Sa 09:00-21:00",
    }
    return RestaurantCreate(**{**data, **changes})

# Creating a restaurant

def test_create_restaurant_returns_new_restaurant(service):
    restaurant = service.create_restaurant(create_request())

    assert restaurant.name == "Taco Town"
    assert restaurant.address == "789 Pine St"
    assert restaurant.description == ""
    assert restaurant.type == "Restaurant"
    assert restaurant.hasMenu is None

def test_create_restaurant_generates_new_id(service):
    restaurant = service.create_restaurant(create_request())

    assert restaurant.id
    assert restaurant.id not in ["1", "2"]

def test_create_restaurant_saves_it_with_existing_restaurants(service, repository):
    restaurant = service.create_restaurant(create_request())

    saved = repository.save_restaurants.call_args.args[0]
    assert [r.id for r in saved] == ["1", "2", restaurant.id]

def test_create_duplicate_restaurant_is_rejected(service, repository):
    with pytest.raises(DuplicateRestaurantError):
        service.create_restaurant(create_request(name="Pizza Palace", address="123 Main St"))

    repository.save_restaurants.assert_not_called()

def test_duplicate_check_ignores_case(service):
    with pytest.raises(DuplicateRestaurantError):
        service.create_restaurant(create_request(name="PIZZA palace", address="123 main st"))

def test_same_name_at_different_address_is_allowed(service):
    restaurant = service.create_restaurant(create_request(name="Pizza Palace", address="999 Elm St"))

    assert restaurant.name == "Pizza Palace"
