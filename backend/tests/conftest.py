import os
import shutil
from pathlib import Path
import tempfile
import pytest
from fastapi.testclient import TestClient
from backend.app.main import main

CURRENT_DIR = Path(__file__).resolve().parent
REAL_DATA = CURRENT_DIR.parent / "data"
TEST_DATA = CURRENT_DIR.parent / "tests/test-data"

#File must be exactly this name to be known as a pytest fixture file.

@pytest.fixture(autouse=True)
def isolated_data():
    files_to_track = ["restaurants.json", "customers.json"]
    
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