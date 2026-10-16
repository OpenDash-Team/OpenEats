from backend.app.repositories.restaurant_repository import RestaurantRepository
from backend.app.schemas.restaurant import Restaurant
from backend.app.schemas.menu_section import MenuSection
from backend.app.schemas.menu_item import MenuItem
from backend.app.schemas.menu_item_request import MenuItemCreate, MenuItemUpdate


class RestaurantService:
    def __init__(self, repository: RestaurantRepository):
        self.repository: RestaurantRepository = repository
    
    def list_restaurants(self):
        return self.repository.get_all_restaurants()

    def _find_restaurant(self, restaurants: list[Restaurant], restaurant_id: str) -> Restaurant:
        for restaurant in restaurants:
            if restaurant.id == restaurant_id:
                return restaurant
        raise ValueError(f"Restaurant with id '{restaurant_id}' is not found")


    def _find_menu_section(self, menu_sections: MenuSection | list[MenuSection], menu_section_id: str) -> MenuSection:
        for menu_section in menu_sections:
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

        new_menu_item = MenuItem(**request.model_dump())    #** means to take all key value pairs in this diciontary and pass them as keyword arguments to the MenuItem constructor.
                                                            #otherwise it will pass the entire dictionary as one positional argument and raise a TypeError.

        if isinstance(menu_section.hasMenuItem, list):
            menu_section.hasMenuItem.append(new_menu_item)
        else:
            menu_section.hasMenuItem = [menu_section.hasMenuItem, new_menu_item]

        self.repository.save_restaurants(restaurants)

        return new_menu_item