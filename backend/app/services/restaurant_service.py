from backend.app.repositories.restaurant_repository import RestaurantRepository
from backend.app.schemas.restaurant import Restaurant
from backend.app.schemas.menu_section import MenuSection
from backend.app.schemas.menu_item import MenuItem
from backend.app.schemas.menu_item_request import MenuItemCreate, MenuItemUpdate
from backend.app.schemas.menu import Menu
from backend.app.schemas.restaurant_request import RestaurantCreate, RestaurantUpdate
from backend.app.core.exceptions import DuplicateRestaurantError, RestaurantNotFoundError

UNCATEGORIZED_MENU_SECTION_ID = "uncategorized"
UNCATEGORIZED_MENU_SECTION_NAME = "Uncategorized"

class RestaurantService:
    def __init__(self, repository: RestaurantRepository):
        self.repository: RestaurantRepository = repository
    
    def list_restaurants(self, name=None, has_menu=None, sort_by=None, sort_desc=False):
        restaurantsList = self.repository.get_all_restaurants()

        if name:
            restaurantsList = [r for r in restaurantsList if name.lower() in r.name.lower()]
        if has_menu is not None:
            restaurantsList = [r for r in restaurantsList if (r.hasMenu is not None) == has_menu]

        if sort_by:
            if sort_by not in Restaurant.model_fields:
                allowed_fields = ", ".join(Restaurant.model_fields.keys())
                raise ValueError(f"Invalid sort_by field: '{sort_by}'. Allowed fields: {allowed_fields}")

            def get_sort_value(r):
                val = getattr(r, sort_by)
                
                if sort_by == "hasMenu":
                    return val is None
                    
                return val if val is not None else ""

            restaurantsList.sort(key=get_sort_value, reverse=sort_desc)
            
        return restaurantsList

    def get_restaurant_by_id(self, restaurant_id: str):
        return self.repository.get_restaurant_by_id(restaurant_id)

    def create_restaurant(self, request: RestaurantCreate) -> Restaurant:
        restaurants = self.repository.get_all_restaurants()
        self._check_not_duplicate(restaurants, request.name, request.address)

        # id, type and hasMenu are filled in by the Restaurant model (new restaurants start with no menu)
        new_restaurant = Restaurant(**request.model_dump())

        restaurants.append(new_restaurant)
        self.repository.save_restaurants(restaurants)

        return new_restaurant

    def update_restaurant(self, restaurant_id: str, request: RestaurantUpdate) -> Restaurant:
        restaurants = self.repository.get_all_restaurants()
        restaurant = next((r for r in restaurants if r.id == restaurant_id), None)

        if restaurant is None:
            raise RestaurantNotFoundError(f"Restaurant with id '{restaurant_id}' is not found")

        # Fields that were not sent (or sent as null) keep their current value
        changes = request.model_dump(exclude_none=True)

        other_restaurants = [r for r in restaurants if r.id != restaurant_id]
        self._check_not_duplicate(other_restaurants, changes.get("name", restaurant.name), changes.get("address", restaurant.address))

        for field, value in changes.items():
            setattr(restaurant, field, value)

        self.repository.save_restaurants(restaurants)

        return restaurant

    def _check_not_duplicate(self, restaurants: list[Restaurant], name: str, address: str) -> None:
        # Chains share names, so a restaurant only counts as a duplicate if the address matches too
        for restaurant in restaurants:
            if restaurant.name.lower() == name.lower() and restaurant.address.lower() == address.lower():
                raise DuplicateRestaurantError(f"A restaurant named '{name}' already exists at '{address}'")

    def _find_restaurant(self, restaurants: list[Restaurant], restaurant_id: str) -> Restaurant:
        for restaurant in restaurants:
            if restaurant.id == restaurant_id:
                return restaurant
        raise ValueError(f"Restaurant with id '{restaurant_id}' is not found")

    def _find_menu_section(self, menu_sections: MenuSection | list[MenuSection], menu_section_id: str) -> MenuSection:
        section_list = (menu_sections if isinstance(menu_sections, list) else [menu_sections])

        for menu_section in section_list:
            if menu_section.id == menu_section_id:
                return menu_section

            if menu_section.hasMenuSection is not None:
                try:
                    return self._find_menu_section(menu_section.hasMenuSection, menu_section_id)

                except ValueError:
                    pass

        raise ValueError(f"MenuSection with id '{menu_section_id}' is not found")

    def add_menu_item(self, restaurant_id: str, request: MenuItemCreate) -> MenuItem:
        restaurants = self.repository.get_all_restaurants()
        restaurant = self._find_restaurant(restaurants, restaurant_id)

        menu_section = self._get_or_create_uncategorized_section(restaurant)
        new_menu_item = MenuItem(**request.model_dump())

        if menu_section.hasMenuItem is None:
            menu_section.hasMenuItem = [new_menu_item]
        elif isinstance(menu_section.hasMenuItem, list):
            menu_section.hasMenuItem.append(new_menu_item)
        else:
            menu_section.hasMenuItem = [menu_section.hasMenuItem, new_menu_item]

        self.repository.save_restaurants(restaurants)

        return new_menu_item

    def update_menu_item(self, restaurant_id: str, menu_item_id: str, request: MenuItemUpdate) -> MenuItem:
        restaurants = self.repository.get_all_restaurants()
        restaurant = self._find_restaurant(restaurants, restaurant_id)

        if restaurant.hasMenu is None:
            raise ValueError(f"MenuItem with id '{menu_item_id}' is not found")

        _, menu_item = self._find_menu_item(restaurant.hasMenu.hasMenuSection, menu_item_id)

        update_data = request.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(menu_item, field, value)

        self.repository.save_restaurants(restaurants)
        return menu_item


    def delete_menu_item(self, restaurant_id: str, menu_item_id: str) -> None:
        restaurants = self.repository.get_all_restaurants()
        restaurant = self._find_restaurant(restaurants, restaurant_id)

        if restaurant.hasMenu is None:
            raise ValueError(f"MenuItem with id '{menu_item_id}' is not found")

        menu_section, menu_item = self._find_menu_item(restaurant.hasMenu.hasMenuSection, menu_item_id)
        menu_items = (menu_section.hasMenuItem if isinstance(menu_section.hasMenuItem, list) else [menu_section.hasMenuItem])
        menu_items.remove(menu_item)
        menu_section.hasMenuItem = menu_items

        self.repository.save_restaurants(restaurants)

    def _get_or_create_uncategorized_section(self, restaurant: Restaurant) -> MenuSection:

        if restaurant.hasMenu is None:
            uncategorized_section = MenuSection(id=UNCATEGORIZED_MENU_SECTION_ID, name=UNCATEGORIZED_MENU_SECTION_NAME, description="", hasMenuItem=[])

            restaurant.hasMenu = Menu(hasMenuSection=[uncategorized_section])

            return uncategorized_section

        menu_sections = (restaurant.hasMenu.hasMenuSection if isinstance(restaurant.hasMenu.hasMenuSection, list) else [restaurant.hasMenu.hasMenuSection])

        for section in menu_sections:
            if section.id == UNCATEGORIZED_MENU_SECTION_ID:
                return section

        uncategorized_section = MenuSection(id=UNCATEGORIZED_MENU_SECTION_ID, name=UNCATEGORIZED_MENU_SECTION_NAME, description="", hasMenuItem=[])

        menu_sections.append(uncategorized_section)
        restaurant.hasMenu.hasMenuSection = menu_sections

        return uncategorized_section


    def _find_menu_item(self,  menu_sections: MenuSection | list[MenuSection], menu_item_id: str) -> tuple[MenuSection, MenuItem]:

        section_list = (menu_sections if isinstance(menu_sections, list) else [menu_sections])

        for section in section_list:
            if section.hasMenuItem is not None:
                menu_items = (section.hasMenuItem if isinstance(section.hasMenuItem, list) else [section.hasMenuItem])

                for item in menu_items:
                    if item.id == menu_item_id:
                        return section, item

            if section.hasMenuSection is not None:
                try:
                    return self._find_menu_item(section.hasMenuSection, menu_item_id)
                except ValueError:
                    pass

        raise ValueError(f"MenuItem with id '{menu_item_id}' is not found")

