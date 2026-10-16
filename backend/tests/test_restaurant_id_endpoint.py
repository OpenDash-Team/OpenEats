import warnings
from pydantic import TypeAdapter
from backend.app.schemas.restaurant import Restaurant

def get_valid_restaurant_id(client):
    """Helper function to grab a real ID from the database for testing."""
    response = client.get("/restaurants")
    data = response.json()
    if response.status_code == 200 and len(data) > 0:
        return data[0]["id"]
    return None

def test_restaurant_id_endpoint_returns_200(client):
    test_id = get_valid_restaurant_id(client)
    
    if not test_id:
        warnings.warn("This couldn't be tested correctly because there were no restaurants.")
        return

    response = client.get(f"/restaurants/{test_id}")
    assert response.status_code == 200, f"Failed! Server returned: {response.json()}"

def test_restaurant_id_endpoint_returns_valid_json(client):
    test_id = get_valid_restaurant_id(client)
    
    if not test_id:
        warnings.warn("This couldn't be tested correctly because there were no restaurants.")
        return

    response = client.get(f"/restaurants/{test_id}")
    assert response.status_code == 200, f"Failed! Server returned: {response.json()}"
    data = response.json()
    
    adapter = TypeAdapter(Restaurant)
    restaurant = adapter.validate_python(data)
    
    assert restaurant.id == test_id

def test_restaurant_id_endpoint_returns_404_for_invalid_id(client):
    response = client.get("/restaurants/this-id-does-not-exist-999")
   
    assert response.status_code == 404, f"Expected 404, but got: {response.status_code}"
    data = response.json()
    assert "detail" in data