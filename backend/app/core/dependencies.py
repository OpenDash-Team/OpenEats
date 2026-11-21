from pathlib import Path

import jwt
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from ..repositories.cart_repository import CartRepository
from ..services.cart_service import CartService

from ..core.security import SECRET_KEY, ALGORITHM
from ..repositories.customer_repository import CustomerRepository
from ..repositories.restaurant_repository import RestaurantRepository
from ..schemas.customer import Customer
from ..services.checkout_service import CheckoutService
from ..repositories.order_repository import OrderRepository
from ..services.customer_service import CustomerService
from ..services.restaurant_service import RestaurantService


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




oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login", auto_error=True)

def get_cart_service() -> CartService:
    cart_repository = CartRepository(get_data_dir() / "carts.json")
    return CartService(cart_repository, get_restaurant_service())

def get_current_customer(
    token: str = Depends(oauth2_scheme),
    customer_service: CustomerService = Depends(get_customer_service),
) -> Customer:

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        customer_id = payload.get("sub")
        token_version = payload.get("ver")
        if not isinstance(customer_id, str) or type(token_version) is not int:
            raise HTTPException(status_code=401, detail="Not authenticated")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Not authenticated")

    customer = customer_service.get_active_customer(customer_id)
    if customer is None or customer.tokenVersion != token_version:
        raise HTTPException(status_code=401, detail="Not authenticated")

    return customer


def require_owner(
    current_customer: Customer = Depends(get_current_customer),
) -> Customer:
    if current_customer.role != "owner":
        raise HTTPException(status_code=403, detail="Owner role required")

    return current_customer

def get_checkout_service() -> CheckoutService:
    cart_repository = CartRepository(get_data_dir() / "carts.json")
    order_repository = OrderRepository(get_data_dir() / "orders.json")
    restaurant_service = get_restaurant_service()
    return CheckoutService(cart_repository=cart_repository, order_repository=order_repository,restaurant_service=restaurant_service,)


def get_order_repository() -> OrderRepository:
    return OrderRepository(get_data_dir() / "orders.json")
