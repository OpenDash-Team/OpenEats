import pytest
from unittest.mock import Mock

from backend.app.core.exceptions import DuplicateRestaurantError, RestaurantNotFoundError
from backend.app.schemas.restaurant import Restaurant
from backend.app.schemas.restaurant_request import RestaurantCreate, RestaurantUpdate
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

# Updating a restaurant

def test_update_changes_only_the_fields_sent(service):
    restaurant = service.update_restaurant("1", RestaurantUpdate(telephone="+1-250-555-0199"))

    assert restaurant.telephone == "+1-250-555-0199"
    assert restaurant.name == "Pizza Palace"
    assert restaurant.address == "123 Main St"
    assert restaurant.openingHours == "Mo-Su 11:00-22:00"

def test_update_keeps_the_same_id(service):
    restaurant = service.update_restaurant("1", RestaurantUpdate(name="Pizza Palace Downtown"))

    assert restaurant.id == "1"

def test_update_ignores_fields_sent_as_null(service):
    restaurant = service.update_restaurant("1", RestaurantUpdate(name=None, address="1 New Rd"))

    assert restaurant.name == "Pizza Palace"
    assert restaurant.address == "1 New Rd"

def test_update_saves_the_change(service, repository):
    service.update_restaurant("1", RestaurantUpdate(name="Pizza Palace Downtown"))

    saved = repository.save_restaurants.call_args.args[0]
    assert saved[0].name == "Pizza Palace Downtown"
    assert saved[1].name == "Burger Barn"

def test_update_unknown_restaurant_is_rejected(service, repository):
    with pytest.raises(RestaurantNotFoundError):
        service.update_restaurant("does-not-exist", RestaurantUpdate(name="New Name"))

    repository.save_restaurants.assert_not_called()

def test_update_into_duplicate_of_another_restaurant_is_rejected(service, repository):
    with pytest.raises(DuplicateRestaurantError):
        service.update_restaurant("1", RestaurantUpdate(name="Burger Barn", address="456 Oak St"))

    repository.save_restaurants.assert_not_called()

def test_update_with_its_own_name_and_address_is_allowed(service):
    restaurant = service.update_restaurant("1", RestaurantUpdate(name="Pizza Palace", address="123 Main St"))

    assert restaurant.name == "Pizza Palace"
