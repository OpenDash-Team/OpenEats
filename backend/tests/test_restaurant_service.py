from backend.app.repositories.restaurant_repository import RestaurantRepository
from backend.app.services.restaurant_service import RestaurantService
from backend.app.schemas.menu_item_request import MenuItemCreate, MenuItemUpdate
from backend.app.schemas.restricted_diet import RestrictedDiet
from backend.app.schemas.offer import Offer
from backend.app.schemas.item_availability import ItemAvailability

def test_add_menu_item(tmp_path):
    from backend.tests.conftest import REAL_DATA

    source_file = REAL_DATA / "restaurants.json"
    test_file = tmp_path / "restaurants.json"

    test_file.write_text(source_file.read_text(encoding="utf-8"), encoding="utf-8")

    repository = RestaurantRepository(test_file)
    service = RestaurantService(repository)

    request = MenuItemCreate(
        name="Test Late",
        description="A test menu item",
        suitableForDiet=RestrictedDiet.VEGETARIAN,
        offers=Offer(
            price=4.99,
            priceCurrency="USD",
            availability=ItemAvailability.IN_STOCK
        )
    )

    new_item = service.add_menu_item(restaurant_id="NwYJoaOHusWdiqXpM7mQH", request=request)

    assert new_item.id is not None
    assert new_item.name == "Test Late"
    assert new_item.description == "A test menu item"

    reloaded_repository = RestaurantRepository(test_file)
    restaurants = reloaded_repository.get_all_restaurants()

    restaurant = next(restaurant for restaurant in restaurants if restaurant.id == "NwYJoaOHusWdiqXpM7mQH")

    menu_sections = (restaurant.hasMenu.hasMenuSection if isinstance(restaurant.hasMenu.hasMenuSection, list) else [restaurant.hasMenu.hasMenuSection])

    uncategorized_section = next(section for section in menu_sections if section.id == "uncategorized")

    menu_items = (uncategorized_section.hasMenuItem if isinstance(uncategorized_section.hasMenuItem, list) else [uncategorized_section.hasMenuItem])

    assert any(item.id == new_item.id for item in menu_items)

def test_update_menu_item(tmp_path):
    from backend.tests.conftest import REAL_DATA

    source_file = REAL_DATA / "restaurants.json"
    test_file = tmp_path / "restaurants.json"
    test_file.write_text(source_file.read_text(encoding="utf-8"), encoding="utf-8")

    repository = RestaurantRepository(test_file)
    service = RestaurantService(repository)

    request = MenuItemUpdate(description="Updated description")
    updated_item = service.update_menu_item(restaurant_id="NwYJoaOHusWdiqXpM7mQH", menu_item_id="F5hn9s3VD9qzKsLV4z8CW", request=request)

    assert updated_item.description == "Updated description"

def test_delete_menu_item(tmp_path):
    from backend.tests.conftest import REAL_DATA

    source_file = REAL_DATA / "restaurants.json"
    test_file = tmp_path / "restaurants.json"

    test_file.write_text(source_file.read_text(encoding="utf-8"), encoding="utf-8")

    repository = RestaurantRepository(test_file)
    service = RestaurantService(repository)

    service.delete_menu_item(restaurant_id="NwYJoaOHusWdiqXpM7mQH", menu_item_id="F5hn9s3VD9qzKsLV4z8CW")

    reloaded_repository = RestaurantRepository(test_file)
    restaurants = reloaded_repository.get_all_restaurants()

    restaurant = next(restaurant for restaurant in restaurants if restaurant.id == "NwYJoaOHusWdiqXpM7mQH")

    section = next(section for section in restaurant.hasMenu.hasMenuSection if section.id == "q9th4Uh9iO6lHbCEJIVz2")

    assert all(item.id != "F5hn9s3VD9qzKsLV4z8CW" for item in section.hasMenuItem)

