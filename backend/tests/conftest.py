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

CURRENT_DIR = Path(__file__).resolve().parent
REAL_DATA = CURRENT_DIR.parent / "data"
TEST_DATA = CURRENT_DIR.parent / "tests/test-data"

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
                return get_customer_service().get_active_customer(customer_id)
            except (CustomerNotFoundError, CustomerDeactivatedError):
                raise HTTPException(status_code=401, detail="Not authenticated")

        app = main()
        app.dependency_overrides[get_current_customer] = fake_current_customer
        return TestClient(app)

    return make_client
