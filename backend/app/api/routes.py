from fastapi import FastAPI, HTTPException, Depends, APIRouter, Path
from json import JSONDecodeError
from ..core.dependencies import get_restaurant_service, get_customer_service, get_current_customer, get_cart_service, require_owner, get_order_repository
from ..schemas.restaurant import Restaurant
from ..schemas.restaurant_query import RestaurantQuery
from ..services.restaurant_service import RestaurantService
from ..schemas.menu_item import MenuItem
from ..schemas.menu_item_request import MenuItemCreate, MenuItemUpdate
from ..schemas.restaurant_request import RestaurantCreate, RestaurantUpdate
from ..core.exceptions import DuplicateRestaurantError, RestaurantNotFoundError, DuplicateEmailError, CustomerNotFoundError, CustomerDeactivatedError, InvalidCredentialsError, MenuItemNotFoundError, MenuItemUnavailableError, DifferentRestaurantError, CartQuantityError, CartItemNotFoundError
from ..schemas.customer import Customer, CustomerResponse
from ..schemas.error import ErrorResponse
from ..schemas.cart import CartResponse
from ..schemas.cart_request import CartItemAdd, CartItemUpdate
from ..services.cart_service import CartService
from ..schemas.customer_request import CustomerCreate, CustomerUpdate
from ..services.customer_service import CustomerService
from ..schemas.login_request import LoginRequest
from ..schemas.token import Token
from ..core import security
from ..core.dependencies import get_checkout_service
from ..services.checkout_service import CheckoutService
from ..schemas.order import Order
from ..core.exceptions import CheckoutValidationError, CheckoutPermissionError
from ..repositories.order_repository import OrderRepository

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

    @api.post(
        "/restaurants/{restaurant_id}/menu-items",
        response_model=MenuItem,
        status_code=201,
        responses={
            401: {"model": ErrorResponse, "description": "Authentication required"},
            403: {"model": ErrorResponse, "description": "Owner role required"},
        },
    )
    def create_menu_item(
        restaurant_id: str,
        request: MenuItemCreate,
        _: Customer = Depends(require_owner),
    ):
        restaurant_service = get_restaurant_service()

        try:
            return restaurant_service.add_menu_item(restaurant_id=restaurant_id, request=request)

        except ValueError as e:
            raise HTTPException(status_code=404, detail=str(e))

    @api.patch(
        "/restaurants/{restaurant_id}/menu-items/{menu_item_id}",
        response_model=MenuItem,
        responses={
            401: {"model": ErrorResponse, "description": "Authentication required"},
            403: {"model": ErrorResponse, "description": "Owner role required"},
        },
    )
    def update_menu_item(
        restaurant_id: str,
        menu_item_id: str,
        request: MenuItemUpdate,
        _: Customer = Depends(require_owner),
    ):
        restaurant_service = get_restaurant_service()

        try:
            return restaurant_service.update_menu_item(restaurant_id=restaurant_id, menu_item_id=menu_item_id, request=request)

        except ValueError as e:
            raise HTTPException(status_code=404,detail=str(e))


    @api.delete(
        "/restaurants/{restaurant_id}/menu-items/{menu_item_id}",
        status_code=204,
        responses={
            401: {"model": ErrorResponse, "description": "Authentication required"},
            403: {"model": ErrorResponse, "description": "Owner role required"},
        },
    )
    def delete_menu_item(
        restaurant_id: str,
        menu_item_id: str,
        _: Customer = Depends(require_owner),
    ):
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
        responses={
            401: {"model": ErrorResponse, "description": "Authentication required"},
            403: {"model": ErrorResponse, "description": "Owner role required"},
            409: {"description": "A restaurant with the same name and address already exists"},
        },
    )
    def create_restaurant(
        request: RestaurantCreate,
        _: Customer = Depends(require_owner),
    ):
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
            401: {"model": ErrorResponse, "description": "Authentication required"},
            403: {"model": ErrorResponse, "description": "Owner role required"},
            404: {"description": "No restaurant has this id"},
            409: {"description": "Another restaurant already has the same name and address"},
        },
    )
    def update_restaurant(
        restaurant_id: str,
        request: RestaurantUpdate,
        _: Customer = Depends(require_owner),
    ):
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
        responses={409: {"model": ErrorResponse, "description": "A customer with this email already exists"}},
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
        responses={401: {"model": ErrorResponse, "description": "Not signed in"}},
    )
    def get_my_customer_info(current_customer: Customer = Depends(get_current_customer)):
        return current_customer


    @api.patch(
        "/customers/me",
        response_model=CustomerResponse,
        summary="Update the signed-in customer's info and delivery address",
        responses={
            401: {"model": ErrorResponse, "description": "Not signed in"},
            409: {"model": ErrorResponse, "description": "Another customer already uses this email"},
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
        responses={401: {"model": ErrorResponse, "description": "Not signed in"}},
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
          
    @api.post(
        "/login",
        response_model=Token,
        status_code=200,
        summary="Login a customer",
        responses={401: {"description": "Invalid credentials or deactivated account"}},
    )
    def login_customer(request: LoginRequest, customer_service: CustomerService = Depends(get_customer_service)):
        """Authenticates a customer and returns a login response."""
        try:
            customer = customer_service.login_customer(request)
            token = security.create_access_token(data={"sub": str(customer.id), "ver": customer.tokenVersion})
            return Token(access_token=token, token_type="bearer")

        except CustomerDeactivatedError as e:
            raise HTTPException(status_code=401, detail=str(e))
        except (InvalidCredentialsError) as e:
            raise HTTPException(status_code=401, detail=str(e))

    @api.post(
    "/logout",
    status_code=200,
    summary="Logout a customer",
    responses={401: {"description": "Not authenticated or token already invalidated"}},
    )
    def logout_customer(
        current_customer: Customer = Depends(get_current_customer),
        customer_service: CustomerService = Depends(get_customer_service),
    ) -> dict[str, str]:
        """Invalidates the customer's current token(s) and logs them out."""
        customer_service.logout_customer(current_customer.id)
        return {"message": "Successfully logged out."}

    @api.get(
        "/cart",
        response_model=CartResponse,
        summary="Get my cart",
        responses={401: {"model": ErrorResponse, "description": "Not signed in"}},
    )
    def get_cart(
        current_customer: Customer = Depends(get_current_customer),
        cart_service: CartService = Depends(get_cart_service),
    ):
        """Returns the signed-in customer's active cart (an empty one is created the first time),
        with current prices and the subtotal and total calculated by the backend."""
        try:
            return cart_service.get_cart(current_customer)

        except CustomerDeactivatedError as e:
            raise HTTPException(status_code=401, detail=str(e))


    @api.post(
        "/cart/items",
        response_model=CartResponse,
        summary="Add a menu item to my cart",
        responses={
            401: {"model": ErrorResponse, "description": "Not signed in"},
            404: {"model": ErrorResponse, "description": "No menu item has this id"},
            409: {"model": ErrorResponse, "description": "The item is out of stock, the cart has items from another restaurant, or it would go over 99"},
        },
    )
    def add_cart_item(
        request: CartItemAdd,
        current_customer: Customer = Depends(get_current_customer),
        cart_service: CartService = Depends(get_cart_service),
    ):
        """Adds the item to the cart. If it's already there, its quantity goes up instead."""
        try:
            return cart_service.add_item(current_customer, request)

        except CustomerDeactivatedError as e:
            raise HTTPException(status_code=401, detail=str(e))

        except MenuItemNotFoundError as e:
            raise HTTPException(status_code=404, detail=str(e))

        except (MenuItemUnavailableError, DifferentRestaurantError, CartQuantityError) as e:
            raise HTTPException(status_code=409, detail=str(e))


    @api.patch(
        "/cart/items/{menu_item_id}",
        response_model=CartResponse,
        summary="Change the quantity of an item in my cart",
        responses={
            401: {"model": ErrorResponse, "description": "Not signed in"},
            404: {"model": ErrorResponse, "description": "The item is not in the cart, or is no longer on the menu"},
            409: {"model": ErrorResponse, "description": "The item is out of stock, so its quantity can only go down"},
        },
    )
    def update_cart_item(
        request: CartItemUpdate,
        menu_item_id: str = Path(description="Id of the menu item in the cart"),
        current_customer: Customer = Depends(get_current_customer),
        cart_service: CartService = Depends(get_cart_service),
    ):
        """Sets the item's quantity (1-99). To take it out of the cart, use DELETE instead."""
        try:
            return cart_service.update_item_quantity(current_customer, menu_item_id, request)

        except CustomerDeactivatedError as e:
            raise HTTPException(status_code=401, detail=str(e))

        except (CartItemNotFoundError, MenuItemNotFoundError) as e:
            raise HTTPException(status_code=404, detail=str(e))

        except MenuItemUnavailableError as e:
            raise HTTPException(status_code=409, detail=str(e))


    @api.delete(
        "/cart/items/{menu_item_id}",
        response_model=CartResponse,
        summary="Remove an item from my cart",
        responses={
            401: {"model": ErrorResponse, "description": "Not signed in"},
            404: {"model": ErrorResponse, "description": "The item is not in the cart"},
        },
    )
    def remove_cart_item(
        menu_item_id: str = Path(description="Id of the menu item in the cart"),
        current_customer: Customer = Depends(get_current_customer),
        cart_service: CartService = Depends(get_cart_service),
    ):
        """Removes the item and returns the updated cart. Works for items that are out of stock or no longer on the menu."""
        try:
            return cart_service.remove_item(current_customer, menu_item_id)

        except CustomerDeactivatedError as e:
            raise HTTPException(status_code=401, detail=str(e))

        except CartItemNotFoundError as e:
            raise HTTPException(status_code=404, detail=str(e))


    @api.delete(
        "/cart",
        response_model=CartResponse,
        summary="Clear my cart",
        responses={401: {"model": ErrorResponse, "description": "Not signed in"}},
    )
    def clear_cart(
        current_customer: Customer = Depends(get_current_customer),
        cart_service: CartService = Depends(get_cart_service),
    ):
        """Removes every item. The cart stays, empty, and can be used for any restaurant again."""
        try:
            return cart_service.clear_cart(current_customer)

        except CustomerDeactivatedError as e:
            raise HTTPException(status_code=401, detail=str(e))


    @api.get(
        "/orders/me",
        response_model=list[Order],
        summary="Get own customer's orders",
        responses={401: {"model": ErrorResponse, "description": "Not signed in"}},
    )
    def get_my_orders(
        current_customer: Customer = Depends(get_current_customer),
        order_repository: OrderRepository = Depends(get_order_repository),
    ):
        return order_repository.get_orders_by_customer(current_customer.id)


    @api.get(
        "/orders/{order_id}",
        response_model=Order,
        summary="Get an order by id",
        responses={404: {"model": ErrorResponse, "description": "Order not found"}},
    )
    def get_order_by_id(
        order_id: str,
        order_repository: OrderRepository = Depends(get_order_repository),
    ):
        order = order_repository.get_order_by_id(order_id)
        if order is None:
            raise HTTPException(status_code=404, detail="Order not found")
        return order


    @api.get(
        "/customers/{customer_id}/orders",
        response_model=list[Order],
        summary="Get orders by customer id",
    )
    def get_orders_by_customer_id(
        customer_id: str,
        order_repository: OrderRepository = Depends(get_order_repository),
    ):
        return order_repository.get_orders_by_customer(customer_id)
    
    @api.post(
        "/checkout",
        response_model=Order,
        status_code=201,
        summary="Checkout the current customer's active cart",
        responses={
            401: { "model": ErrorResponse, "description": "Not authenticated",},
            403: {"model": ErrorResponse, "description": "Customer cannot check out",},
            409: {"model": ErrorResponse, "description": "Cart or menu validation failed",},
        },
    )
    def checkout(
        current_customer: Customer = Depends(get_current_customer),
        checkout_service: CheckoutService = Depends(get_checkout_service),
    ):
        """
        Validates the current cart, recalculates prices,
        persists an order, and then closes the cart.
        """

        try:
            return checkout_service.checkout(current_customer)

        except CheckoutPermissionError as e:
            raise HTTPException(status_code=403, detail=str(e),) from e

        except CheckoutValidationError as e:
            raise HTTPException(status_code=409, detail=str(e),) from e


    @api.get("/", include_in_schema=False)
    @api.get("/{path:path}", include_in_schema=False)
    def api_not_found(path: str):
        raise HTTPException(status_code=404, detail="Not Found")
