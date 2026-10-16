import pytest
from unittest.mock import Mock

from backend.app.schemas.restaurant import Restaurant
from backend.app.schemas.menu import Menu 
from backend.app.services.restaurant_service import RestaurantService
@pytest.fixture
def dummy_restaurants():
    menu = Menu.model_construct()
    
    return [
        Restaurant(id="1", name="Alpha Bites", address="123 Main St", telephone="111", openingHours="9-5", hasMenu=menu, type="restaurant"),
        Restaurant(id="2", name="Zeta Grill", address="456 Oak St", telephone="222", openingHours="10-10", hasMenu=None, type="restaurant"),
        Restaurant(id="3", name="Beta Bakery", address="789 Pine St", telephone="333", openingHours="6-2", hasMenu=menu, type="restaurant"),
        Restaurant(id="4", name="Alpha Cafe", address="321 Elm St", telephone="444", openingHours="8-4", hasMenu=None, type="restaurant"),
    ]
@pytest.fixture
def mock_repository(dummy_restaurants):
    repo = Mock()
    repo.get_all_restaurants.return_value = dummy_restaurants
    return repo

@pytest.fixture
def restaurant_service(mock_repository):
    return RestaurantService(repository=mock_repository)


class TestRestaurantService:

    def test_list_restaurants_no_filters(self, restaurant_service, dummy_restaurants):

        results = restaurant_service.list_restaurants()
        
        assert len(results) == 4
        assert results == dummy_restaurants
        restaurant_service.repository.get_all_restaurants.assert_called_once()

    def test_filter_by_name_exact_match(self, restaurant_service):
        results = restaurant_service.list_restaurants(name="Zeta Grill")
        assert len(results) == 1
        assert results[0].name == "Zeta Grill"

    def test_filter_by_name_partial_case_insensitive(self, restaurant_service):
        results = restaurant_service.list_restaurants(name="aLpHa")
        assert len(results) == 2
        names = [r.name for r in results]
        assert "Alpha Bites" in names
        assert "Alpha Cafe" in names

    def test_filter_by_has_menu_true(self, restaurant_service):
        results = restaurant_service.list_restaurants(has_menu=True)
        assert len(results) == 2
        for r in results:
            assert r.hasMenu is not None

    def test_filter_by_has_menu_false(self, restaurant_service):
        results = restaurant_service.list_restaurants(has_menu=False)
        assert len(results) == 2
        for r in results:
            assert r.hasMenu is None

    def test_sort_by_name_ascending(self, restaurant_service):
        results = restaurant_service.list_restaurants(sort_by="name", sort_desc=False)
        assert len(results) == 4
        assert results[0].name == "Alpha Bites"
        assert results[1].name == "Alpha Cafe"
        assert results[2].name == "Beta Bakery"
        assert results[3].name == "Zeta Grill"

    def test_sort_by_name_descending(self, restaurant_service):
        results = restaurant_service.list_restaurants(sort_by="name", sort_desc=True)
        assert len(results) == 4
        assert results[0].name == "Zeta Grill"
        assert results[1].name == "Beta Bakery"
        assert results[2].name == "Alpha Cafe"
        assert results[3].name == "Alpha Bites"

    def test_sort_by_invalid_attribute(self, restaurant_service, dummy_restaurants):
        with pytest.raises(ValueError) as exc_info:
            restaurant_service.list_restaurants(sort_by="non_existent_field")
        assert "Invalid sort_by" in str(exc_info.value)
        
    def test_combine_filter_and_sort(self, restaurant_service):
        results = restaurant_service.list_restaurants(name="Alpha", sort_by="name", sort_desc=True)
        
        assert len(results) == 2
        assert results[0].name == "Alpha Cafe"
        assert results[1].name == "Alpha Bites"