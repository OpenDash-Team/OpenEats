from fastapi import FastAPI, HTTPException, Depends
from json import JSONDecodeError

from backend.app.core.dependencies import get_restaurant_service
from backend.app.schemas.restaurant import Restaurant
from backend.app.schemas.restaurant_query import RestaurantQuery
from backend.app.services.restaurant_service import RestaurantService
from backend.app.schemas.menu_item import MenuItem
from backend.app.schemas.menu_item_request import MenuItemCreate, MenuItemUpdate
from backend.app.schemas.restaurant_request import RestaurantCreate, RestaurantUpdate
from backend.app.core.exceptions import DuplicateRestaurantError, RestaurantNotFoundError

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

    @app.patch("/restaurants/{restaurant_id}/menu-items/{menu_item_id}", response_model=MenuItem)
    def update_menu_item(restaurant_id: str, menu_item_id: str, request: MenuItemUpdate):
        restaurant_service = get_restaurant_service()

        try:
            return restaurant_service.update_menu_item(restaurant_id=restaurant_id, menu_item_id=menu_item_id, request=request)

        except ValueError as e:
            raise HTTPException(status_code=404,detail=str(e))


    @app.delete("/restaurants/{restaurant_id}/menu-items/{menu_item_id}", status_code=204)
    def delete_menu_item(restaurant_id: str, menu_item_id: str):
        restaurant_service = get_restaurant_service()

        try:
            restaurant_service.delete_menu_item(restaurant_id=restaurant_id, menu_item_id=menu_item_id)

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


    @app.post(
        "/restaurants",
        response_model=Restaurant,
        status_code=201,
        summary="Create a restaurant",
        responses={409: {"description": "A restaurant with the same name and address already exists"}},
    )
    def create_restaurant(request: RestaurantCreate):
        """Creates a new restaurant. The server generates its id, and it starts with no menu."""
        restaurant_service = get_restaurant_service()

        try:
            return restaurant_service.create_restaurant(request)

        except DuplicateRestaurantError as e:
            raise HTTPException(status_code=409, detail=str(e))


    @app.patch(
        "/restaurants/{restaurant_id}",
        response_model=Restaurant,
        summary="Update a restaurant's information",
        responses={
            404: {"description": "No restaurant has this id"},
            409: {"description": "Another restaurant already has the same name and address"},
        },
    )
    def update_restaurant(restaurant_id: str, request: RestaurantUpdate):
        """Changes only the fields that are sent. The id and menu can't be changed here."""
        restaurant_service = get_restaurant_service()

        try:
            return restaurant_service.update_restaurant(restaurant_id, request)

        except RestaurantNotFoundError as e:
            raise HTTPException(status_code=404, detail=str(e))

        except DuplicateRestaurantError as e:
            raise HTTPException(status_code=409, detail=str(e))
