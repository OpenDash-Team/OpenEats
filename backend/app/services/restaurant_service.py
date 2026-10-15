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

        if sort_by and sort_by in Restaurant.model_fields:
            restaurantsList.sort(
                key=lambda r: getattr(r, sort_by), 
                reverse=sort_desc
            )
            
        return restaurantsList