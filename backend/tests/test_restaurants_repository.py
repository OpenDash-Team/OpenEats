import json
import pytest
from pathlib import Path
from unittest.mock import patch, mock_open
from backend.app.repositories.restaurant_repository import RestaurantRepository

def test_repository_handles_missing_file(tmp_path):
    missing_file = tmp_path / "missing_file.json"
    repo = RestaurantRepository(missing_file)
    
    # Catch the warning and verify it matches the expected text
    with pytest.warns(UserWarning):
        results = repo.get_all_restaurants()
    
    assert results == []

@patch("pathlib.Path.exists", return_value=True)
def test_repository_loads_valid_data(mock_exists):
    valid_json = """[{
        "type": "Restaurant",
        "id": "123",
        "name": "Test Restaurant",
        "address": "123 Main St",
        "telephone": "555-0100",
        "openingHours": "Mo-Su 09:00-17:00",
        "hasMenu": {
            "type": "Menu",
            "id": "456",
            "hasMenuSection": [],
            "hasMenuItem": []
        }
    }]"""
    
    with patch("builtins.open", mock_open(read_data=valid_json)):
        repo = RestaurantRepository(Path("dummy.json"))
        results = repo.get_all_restaurants()
        
        assert len(results) == 1
        assert results[0].name == "Test Restaurant"

@patch("pathlib.Path.exists", return_value=True)
def test_repository_rejects_invalid_schema(mock_exists):
    invalid_json = """[{
        "type": "Restaurant",
        "id": "123",
        "name": "Missing Address and Menu Restaurant"
    }]"""
    
    with patch("builtins.open", mock_open(read_data=invalid_json)):
        repo = RestaurantRepository(Path("dummy.json"))
        
        with pytest.raises(ValueError):
            repo.get_all_restaurants()
            
            
def test_repository_loads_real_data():
    from backend.tests.conftest import REAL_DATA
    real_data_path = REAL_DATA / "restaurants.json"
    
    repo = RestaurantRepository(real_data_path)
    results = repo.get_all_restaurants()
    
    assert len(results) >= 2
    assert results[0].name is not None
    assert results[0].id is not None


def test_repository_saves_restaurants(tmp_path):
    from backend.tests.conftest import REAL_DATA

    source_repo = RestaurantRepository(REAL_DATA / "restaurants.json")
    restaurants = source_repo.get_all_restaurants()

    output_file = tmp_path / "restaurants.json"
    output_repo = RestaurantRepository(output_file)

    output_repo.save_restaurants(restaurants)

    assert output_file.exists()

    reloaded = output_repo.get_all_restaurants()

    assert len(reloaded) == len(restaurants)
    assert reloaded[0].id == restaurants[0].id
    assert reloaded[0].name == restaurants[0].name