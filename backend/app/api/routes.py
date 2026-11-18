from fastapi import FastAPI, HTTPException, Depends, APIRouter
from json import JSONDecodeError

from ..core.dependencies import get_restaurant_service, get_customer_service, get_current_customer, get_cart_service
from ..schemas.restaurant import Restaurant
from ..schemas.restaurant_query import RestaurantQuery
from ..services.restaurant_service import RestaurantService
from ..schemas.menu_item import MenuItem
from ..schemas.menu_item_request import MenuItemCreate, MenuItemUpdate
from ..schemas.restaurant_request import RestaurantCreate, RestaurantUpdate
from ..core.exceptions import DuplicateRestaurantError, RestaurantNotFoundError, DuplicateEmailError, CustomerNotFoundError, CustomerDeactivatedError
from ..schemas.customer import Customer, CustomerResponse
from ..schemas.customer_request import CustomerCreate, CustomerUpdate
from ..services.customer_service import CustomerService
from ..schemas.cart import CartResponse
from ..schemas.cart_request import CartItemAdd, CartItemUpdate
from ..services.cart_service import CartService
from ..core.exceptions import MenuItemNotFoundError, MenuItemUnavailableError, DifferentRestaurantError, CartItemNotFoundError, CartQuantityError

# Status code for each error the cart service can raise
CART_ERROR_STATUS = {
    MenuItemNotFoundError: 404,
    CartItemNotFoundError: 404,
    MenuItemUnavailableError: 409,
    DifferentRestaurantError: 409,
    CartQuantityError: 422,
    CustomerDeactivatedError: 403,
}
CART_ERRORS = tuple(CART_ERROR_STATUS)
CART_ERROR_RESPONSES = {
    401: {"description": "Not signed in"},
    403: {"description": "The customer's account is deactivated"},
}

def create_routes(api: FastAPI | APIRouter):
    @api.get("/health")
    async def health():
        return {"status": "ok"}

    @api.get("/restaurants", response_model=list[Restaurant])
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

    @api.post("/restaurants/{restaurant_id}/menu-items", response_model=MenuItem, status_code=201)
    def create_menu_item(restaurant_id: str, request: MenuItemCreate):
        restaurant_service = get_restaurant_service()

        try:
            return restaurant_service.add_menu_item(restaurant_id=restaurant_id, request=request)

        except ValueError as e:
            raise HTTPException(status_code=404, detail=str(e))

    @api.patch("/restaurants/{restaurant_id}/menu-items/{menu_item_id}", response_model=MenuItem)
    def update_menu_item(restaurant_id: str, menu_item_id: str, request: MenuItemUpdate):
        restaurant_service = get_restaurant_service()

        try:
            return restaurant_service.update_menu_item(restaurant_id=restaurant_id, menu_item_id=menu_item_id, request=request)

        except ValueError as e:
            raise HTTPException(status_code=404,detail=str(e))


    @api.delete("/restaurants/{restaurant_id}/menu-items/{menu_item_id}", status_code=204)
    def delete_menu_item(restaurant_id: str, menu_item_id: str):
        restaurant_service = get_restaurant_service()

        try:
            restaurant_service.delete_menu_item(restaurant_id=restaurant_id, menu_item_id=menu_item_id)

            return None

        except ValueError as e:
            raise HTTPException(status_code=404, detail=str(e))

    @api.get("/restaurants/{restaurant_id}", response_model=Restaurant)
    def get_restaurant(restaurant_id: str):
        restaurant_service = get_restaurant_service()
    
        try:
            restaurant = restaurant_service.get_restaurant_by_id(restaurant_id)
            if not restaurant:
                raise HTTPException(status_code=404, detail="Restaurant not found")
            return restaurant
        except JSONDecodeError:
            raise HTTPException(status_code=500, detail="Invalid JSON data")


    @api.post(
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


    @api.patch(
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


    @api.post(
        "/customers",
        response_model=CustomerResponse,
        status_code=201,
        summary="Register a customer",
        responses={409: {"description": "A customer with this email already exists"}},
    )
    def register_customer(request: CustomerCreate, customer_service: CustomerService = Depends(get_customer_service)):
        """Creates a new customer account. The password is stored hashed and never returned."""
        try:
            return customer_service.register_customer(request)

        except DuplicateEmailError as e:
            raise HTTPException(status_code=409, detail=str(e))


    @api.get(
        "/customers/me",
        response_model=CustomerResponse,
        summary="Get the signed-in customer's info",
        responses={401: {"description": "Not signed in"}},
    )
    def get_my_customer_info(current_customer: Customer = Depends(get_current_customer)):
        return current_customer


    @api.patch(
        "/customers/me",
        response_model=CustomerResponse,
        summary="Update the signed-in customer's info and delivery address",
        responses={
            401: {"description": "Not signed in"},
            409: {"description": "Another customer already uses this email"},
        },
    )
    def update_my_customer_info(
        request: CustomerUpdate,
        current_customer: Customer = Depends(get_current_customer),
        customer_service: CustomerService = Depends(get_customer_service),
    ):
        """Changes only the fields that are sent. The password, role and id can't be changed here."""
        try:
            return customer_service.update_customer(current_customer.id, request)

        except DuplicateEmailError as e:
            raise HTTPException(status_code=409, detail=str(e))

        except (CustomerNotFoundError, CustomerDeactivatedError) as e:
            raise HTTPException(status_code=401, detail=str(e))


    @api.delete(
        "/customers/me",
        status_code=204,
        summary="Deactivate the signed-in customer's account",
        responses={401: {"description": "Not signed in"}},
    )
    def deactivate_my_account(
        current_customer: Customer = Depends(get_current_customer),
        customer_service: CustomerService = Depends(get_customer_service),
    ):
        """The account is kept (so past orders stay valid) but marked inactive, so it can't be used again."""
        try:
            customer_service.deactivate_customer(current_customer.id)

        except (CustomerNotFoundError, CustomerDeactivatedError) as e:
            raise HTTPException(status_code=401, detail=str(e))


    @api.get(
        "/cart",
        response_model=CartResponse,
        summary="Get my cart",
        responses=CART_ERROR_RESPONSES,
    )
    def get_cart(current_customer: Customer = Depends(get_current_customer), cart_service: CartService = Depends(get_cart_service)):
        """Returns the signed-in customer's active cart (an empty one is created if they don't have one),
        with current prices and the subtotal and total calculated by the backend."""
        try:
            return cart_service.get_cart(current_customer)

        except CART_ERRORS as e:
            raise HTTPException(status_code=CART_ERROR_STATUS[type(e)], detail=str(e))


    @api.post(
        "/cart/items",
        response_model=CartResponse,
        summary="Add a menu item to my cart",
        responses={
            **CART_ERROR_RESPONSES,
            404: {"description": "No menu item has this id"},
            409: {"description": "The item is out of stock, or the cart has items from another restaurant"},
            422: {"description": "Invalid quantity, or more than 99 of one item"},
        },
    )
    def add_cart_item(request: CartItemAdd, current_customer: Customer = Depends(get_current_customer), cart_service: CartService = Depends(get_cart_service)):
        """Adds the item to the cart. If it's already there, its quantity goes up instead."""
        try:
            return cart_service.add_item(current_customer, request)

        except CART_ERRORS as e:
            raise HTTPException(status_code=CART_ERROR_STATUS[type(e)], detail=str(e))


    @api.patch(
        "/cart/items/{menu_item_id}",
        response_model=CartResponse,
        summary="Change the quantity of an item in my cart",
        responses={
            **CART_ERROR_RESPONSES,
            404: {"description": "The item is not in the cart"},
            409: {"description": "The item is out of stock now (it can still be removed)"},
        },
    )
    def update_cart_item(menu_item_id: str, request: CartItemUpdate, current_customer: Customer = Depends(get_current_customer), cart_service: CartService = Depends(get_cart_service)):
        try:
            return cart_service.update_item_quantity(current_customer, menu_item_id, request)

        except CART_ERRORS as e:
            raise HTTPException(status_code=CART_ERROR_STATUS[type(e)], detail=str(e))


    @api.delete(
        "/cart/items/{menu_item_id}",
        response_model=CartResponse,
        summary="Remove an item from my cart",
        responses={**CART_ERROR_RESPONSES, 404: {"description": "The item is not in the cart"}},
    )
    def remove_cart_item(menu_item_id: str, current_customer: Customer = Depends(get_current_customer), cart_service: CartService = Depends(get_cart_service)):
        try:
            return cart_service.remove_item(current_customer, menu_item_id)

        except CART_ERRORS as e:
            raise HTTPException(status_code=CART_ERROR_STATUS[type(e)], detail=str(e))


    @api.delete(
        "/cart",
        response_model=CartResponse,
        summary="Clear my cart",
        responses=CART_ERROR_RESPONSES,
    )
    def clear_cart(current_customer: Customer = Depends(get_current_customer), cart_service: CartService = Depends(get_cart_service)):
        """Removes every item. The cart itself stays, empty, and can be used for any restaurant again."""
        try:
            return cart_service.clear_cart(current_customer)

        except CART_ERRORS as e:
            raise HTTPException(status_code=CART_ERROR_STATUS[type(e)], detail=str(e))


    @api.get("/", include_in_schema=False)
    @api.get("/{path:path}", include_in_schema=False)
    def api_not_found(path: str):
        raise HTTPException(status_code=404, detail="Not Found")