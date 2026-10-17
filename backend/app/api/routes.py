from fastapi import FastAPI, HTTPException, Depends
from json import JSONDecodeError

from backend.app.core.dependencies import get_restaurant_service
from backend.app.schemas.restaurant import Restaurant
from backend.app.schemas.restaurant_query import RestaurantQuery
from backend.app.services.restaurant_service import RestaurantService
from backend.app.schemas.menu_item import MenuItem
from backend.app.schemas.menu_item_request import MenuItemCreate, MenuItemUpdate

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
        except ValueError as e:
            if "Invalid sort_by" in str(e):
                raise HTTPException(status_code=400, detail=str(e))
            raise HTTPException(status_code=500, detail="Restaurant data failed to follow correct list[Restaurant] schema")

    @app.post("/restaurants/{restaurant_id}/menu-items", response_model=MenuItem, status_code=201)
    def create_menu_item(restaurant_id: str, request: MenuItemCreate):
        restaurant_service = get_restaurant_service()

        try:
            return restaurant_service.add_menu_item(restaurant_id=restaurant_id, request=request)

        except ValueError as e:
            raise HTTPException(status_code=404, detail=str(e))

    @app.patch("/restaurants/{restaurant_id}/menu-sections/{menu_section_id}/items/{menu_item_id}", response_model=MenuItem)
    def update_menu_item(restaurant_id: str, menu_section_id: str, menu_item_id: str, request: MenuItemUpdate):
        restaurant_service = get_restaurant_service()

        try:
            return restaurant_service.update_menu_item(restaurant_id=restaurant_id, menu_section_id=menu_section_id, menu_item_id=menu_item_id, request=request)

        except ValueError as e:
            raise HTTPException(status_code=404,detail=str(e))


    @app.delete("/restaurants/{restaurant_id}/menu-sections/{menu_section_id}/items/{menu_item_id}", status_code=204)
    def delete_menu_item(restaurant_id: str, menu_section_id: str, menu_item_id: str):
        restaurant_service = get_restaurant_service()

        try:
            restaurant_service.delete_menu_item(restaurant_id=restaurant_id, menu_section_id=menu_section_id, menu_item_id=menu_item_id)

            return None

        except ValueError as e:
            raise HTTPException(status_code=404, detail=str(e))

    @app.get("/restaurants/{restaurant_id}", response_model=Restaurant)
    def get_restaurant(restaurant_id: str):
        restaurant_service = get_restaurant_service()
    
        try:
            restaurant = restaurant_service.get_restaurant_by_id(restaurant_id)
            if not restaurant:
                raise HTTPException(status_code=404, detail="Restaurant not found")
            return restaurant
        except JSONDecodeError:
            raise HTTPException(status_code=500, detail="Invalid JSON data")
