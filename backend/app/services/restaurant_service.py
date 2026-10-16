from backend.app.repositories.restaurant_repository import RestaurantRepository
from backend.app.schemas.restaurant import Restaurant


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
                    return val is not None
                    
                return val if val is not None else ""

            restaurantsList.sort(key=get_sort_value, reverse=sort_desc)
            
        return restaurantsList

    def get_restaurant_by_id(self, restaurant_id: str):
        return self.repository.get_restaurant_by_id(restaurant_id)