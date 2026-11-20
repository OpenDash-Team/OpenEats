from pathlib import Path

from fastapi import HTTPException

from ..services.restaurant_service import RestaurantService
from ..services.customer_service import CustomerService
from ..services.cart_service import CartService
from ..repositories.restaurant_repository import RestaurantRepository
from ..repositories.customer_repository import CustomerRepository
from ..repositories.cart_repository import CartRepository
from ..schemas.customer import Customer
from ..services.checkout_service import CheckoutService
from ..repositories.order_repository import OrderRepository

def get_data_dir() -> Path:
    data_dir = Path(__file__).resolve().parents[2] / "data"

    if not data_dir.exists():
        data_dir.mkdir()

    return data_dir

def get_restaurant_service():
    restaurant_repository = RestaurantRepository(get_data_dir() / "restaurants.json")
    return RestaurantService(restaurant_repository)

def get_customer_service() -> CustomerService:
    customer_repository = CustomerRepository(get_data_dir() / "customers.json")
    return CustomerService(customer_repository)

def get_cart_service() -> CartService:
    cart_repository = CartRepository(get_data_dir() / "carts.json")
    return CartService(cart_repository, get_restaurant_service())

def get_current_customer() -> Customer:
    """Placeholder until login (#52) is merged: rejects every request."""
    raise HTTPException(status_code=401, detail="Not authenticated", headers={"WWW-Authenticate": "Bearer"})

def get_checkout_service() -> CheckoutService:
    cart_repository = CartRepository(get_data_dir() / "carts.json")
    order_repository = OrderRepository(get_data_dir() / "orders.json")
    restaurant_service = get_restaurant_service()
    return CheckoutService(cart_repository=cart_repository, order_repository=order_repository,restaurant_service=restaurant_service,)