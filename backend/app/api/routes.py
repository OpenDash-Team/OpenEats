from fastapi import FastAPI, HTTPException, Depends
from json import JSONDecodeError

from backend.app.core.dependencies import get_restaurant_service
from backend.app.schemas.restaurant import Restaurant
from backend.app.schemas.restaurant_query import RestaurantQuery
from backend.app.services.restaurant_service import RestaurantService

def create_routes(app: FastAPI):
    @app.get("/health")
    async def health():
        return {"status": "ok"}

    @app.get("/restaurants", response_model=list[Restaurant])
    def list_restaurants(params: RestaurantQuery = Depends()):
        restaurant_service = get_restaurant_service()
    
        try:
            return restaurant_service.list_restaurants(
                name=params.name,
                has_menu=params.hasMenu,
                sort_by=params.sort_by,
                sort_desc=params.sort_desc
            )

        except JSONDecodeError:
            raise HTTPException(status_code=500, detail="Restaurant data failed to due to invalid JSON")
        except ValueError:
            raise HTTPException(status_code=500, detail="Restaurant data failed to follow correct list[Restaurant] schema")


    @app.get("/restaurant/{restaurant_id}", response_model=Restaurant)
    def get_restaurant(restaurant_id: str):
        restaurant_service = get_restaurant_service()
    
        try:
            restaurant = restaurant_service.get_restaurant_by_id(restaurant_id)
            if not restaurant:
                raise HTTPException(status_code=404, detail="Restaurant not found")
            return restaurant
        except JSONDecodeError:
            raise HTTPException(status_code=500, detail="Invalid JSON data")