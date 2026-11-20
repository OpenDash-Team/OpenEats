import os
import shutil
from pathlib import Path
import tempfile
import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient
from backend.app.main import main
from backend.app.core.dependencies import get_current_customer, get_customer_service
from backend.app.core.exceptions import CustomerDeactivatedError, CustomerNotFoundError

from decimal import Decimal
from backend.app.repositories.cart_repository import CartRepository
from backend.app.repositories.order_repository import OrderRepository
from backend.app.repositories.restaurant_repository import RestaurantRepository
from backend.app.services.checkout_service import CheckoutService
from backend.app.services.restaurant_service import RestaurantService
from backend.app.schemas.customer import Customer
from backend.app.schemas.cart import Cart, CartItem
from backend.app.schemas.restaurant import Restaurant
from backend.app.schemas.menu import Menu
from backend.app.schemas.menu_section import MenuSection
from backend.app.schemas.menu_item import MenuItem
from backend.app.schemas.offer import Offer
from backend.app.schemas.item_availability import ItemAvailability
from backend.app.schemas.restricted_diet import RestrictedDiet

CURRENT_DIR = Path(__file__).resolve().parent
REAL_DATA = CURRENT_DIR.parent / "data"
TEST_DATA = CURRENT_DIR.parent / "tests/test-data"
OWNER_ID = "cust0000000000000owner"

#File must be exactly this name to be known as a pytest fixture file.

@pytest.fixture(autouse=True)
def isolated_data():
    files_to_track = ["restaurants.json", "customers.json", "carts.json"]
    
    for name in files_to_track:
        test_file = TEST_DATA / name
        if not test_file.exists():
            pytest.exit(f"CRITICAL ABORT: Missing required test file '{test_file}'. Please create the test-data folder and add {name}.")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        backup_path = Path(temp_dir)
        
        for name in files_to_track:
            if (REAL_DATA / name).exists():
                shutil.copy(REAL_DATA / name, backup_path / name)
                
        for name in files_to_track:
            shutil.copy(TEST_DATA / name, REAL_DATA / name)
            
        yield
        
        for name in files_to_track:
            if (backup_path / name).exists():
                shutil.copy(backup_path / name, REAL_DATA / name)
            elif (REAL_DATA / name).exists():
                os.remove(REAL_DATA / name)

@pytest.fixture
def client():
    app = main()
    return TestClient(app)


@pytest.fixture
def sign_in_as():
    """Gives a function that makes a test client signed in as the given customer id.

    Login (JWT) is a separate task, so this replaces get_current_customer the same way the
    real one will work: look the customer up and answer 401 if they're missing or deactivated.
    """
    def make_client(customer_id):
        def fake_current_customer():
            try:
                customer = get_customer_service().get_active_customer(customer_id)
            except (CustomerNotFoundError, CustomerDeactivatedError):
                raise HTTPException(status_code=401, detail="Not authenticated")
            if customer is None:
                raise HTTPException(status_code=401, detail="Not authenticated")
            return customer

        app = main()
        app.dependency_overrides[get_current_customer] = fake_current_customer
        return TestClient(app)

    return make_client
@pytest.fixture
def owner_client(sign_in_as):
    return sign_in_as(OWNER_ID)

@pytest.fixture
<<<<<<< HEAD
def owner_client(sign_in_as):
    return sign_in_as(OWNER_ID)
=======
def checkout_setup(tmp_path):
    (service, customer, cart_repo, order_repo, _, _,) = checkout_setup
    app = main()
    app.dependency_overrides[get_current_customer] = (lambda: customer)
    app.dependency_overrides[get_checkout_service] = (lambda: service)

    try:
        with TestClient(app) as client:
            response = client.post("/api/v1/checkout")

        assert response.status_code == 201
        data = response.json()
        assert data["customerId"] == customer.id
        assert data["total"] == "10.98"
        orders = order_repo.get_all_orders()
        carts = cart_repo.get_all_carts()
        assert len(orders) == 1
        assert orders[0].id == data["id"]
        assert orders[0].total == Decimal("10.98")
        assert carts[0].status == "checkedOut"

    finally:
        app.dependency_overrides.clear()
>>>>>>> origin/feature/Checkout-and-Initial-Order-Creation
