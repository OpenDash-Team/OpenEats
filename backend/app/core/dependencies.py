from pathlib import Path

import jwt
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer

from ..core.exceptions import CustomerNotFoundError
from ..core.security import SECRET_KEY, ALGORITHM
from ..repositories.customer_repository import CustomerRepository
from ..repositories.restaurant_repository import RestaurantRepository
from ..schemas.customer import Customer
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




oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login", auto_error=False)


def get_current_customer(
    token: str | None = Depends(oauth2_scheme),
    customer_service: CustomerService = Depends(get_customer_service),
) -> Customer | None:
    if token is None:
        return None

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.InvalidTokenError:
        return None

    customer_id = payload.get("sub")
    if not isinstance(customer_id, str):
        return None

    try:
        return customer_service.get_customer(customer_id)
    except CustomerNotFoundError:
        return None
