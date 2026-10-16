from backend.app.repositories.restaurant_repository import RestaurantRepository
from backend.app.schemas.restaurant import Restaurant
from backend.app.schemas.menu_section import MenuSection
from backend.app.schemas.menu_item import MenuItem
from backend.app.schemas.menu_item_request import MenuItemCreate, MenuItemUpdate

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

    def add_menu_item(self, restaurant_id: str, menu_section_id: str, request: MenuItemCreate) -> MenuItem:
        restaurants = self.repository.get_all_restaurants()
        restaurant = self._find_restaurant(restaurants, restaurant_id)

        menu_section = self._find_menu_section(restaurant.hasMenu.hasMenuSection, menu_section_id)
        new_menu_item = MenuItem(**request.model_dump())    

        if isinstance(menu_section.hasMenuItem, list):
            menu_section.hasMenuItem.append(new_menu_item)
        else:
            menu_section.hasMenuItem = [menu_section.hasMenuItem, new_menu_item]

        self.repository.save_restaurants(restaurants)

        return new_menu_item

    def update_menu_item(self, restaurant_id: str, menu_section_id: str, menu_item_id: str, request: MenuItemUpdate) -> MenuItem:
        restaurants = self.repository.get_all_restaurants()
        restaurant = self._find_restaurant(restaurants, restaurant_id)
        menu_section = self._find_menu_section(restaurant.hasMenu.hasMenuSection, menu_section_id)
        menu_items = (menu_section.hasMenuItem if isinstance(menu_section.hasMenuItem, list) else [menu_section.hasMenuItem])

        for menu_item in menu_items:
            if menu_item.id == menu_item_id:
                update_data = request.model_dump(exclude_unset=True)

                for field, value in update_data.items():
                    setattr(menu_item, field, value)

                self.repository.save_restaurants(restaurants)

                return menu_item

        raise ValueError(f"MenuItem with id '{menu_item_id}' is not found")

    def delete_menu_item(self, restaurant_id: str, menu_section_id: str, menu_item_id: str) -> None:
        restaurants = self.repository.get_all_restaurants()
        restaurant = self._find_restaurant(restaurants, restaurant_id)

        menu_section = self._find_menu_section(restaurant.hasMenu.hasMenuSection, menu_section_id)
        menu_items = (menu_section.hasMenuItem if isinstance(menu_section.hasMenuItem, list) else [menu_section.hasMenuItem])

        for menu_item in menu_items:
            if menu_item.id == menu_item_id:
                menu_items.remove(menu_item)
                menu_section.hasMenuItem = menu_items

                self.repository.save_restaurants(restaurants)
                return

        raise ValueError(f"MenuItem with id '{menu_item_id}' is not found")