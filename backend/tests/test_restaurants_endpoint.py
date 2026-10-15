import os
import warnings
from pydantic import TypeAdapter
from backend.app.schemas.restaurant import Restaurant

def test_restaurants_endpoint_returns_200(client):
    
    response = client.get("/restaurants")
    assert response.status_code == 200, f"Failed! Server returned: {response.json()}"
    
def test_restaurants_endpoint_returns_valid_json(client):
    response = client.get("/restaurants")
    assert response.status_code == 200, f"Failed! Server returned: {response.json()}"
    data = response.json()
    
    adapter = TypeAdapter(list[Restaurant])
    
    restaurants = adapter.validate_python(data)
    
    if len(restaurants) == 0:
        warnings.warn("This couldn't be tested correctly because there were no restaurants.")

def test_restaurants_endpoint_with_name_query(client):
    response = client.get("/restaurants?name=Startbucks")
    assert response.status_code == 200, f"Failed! Server returned: {response.json()}"
    data = response.json()
    
    adapter = TypeAdapter(list[Restaurant])
    
    restaurants = adapter.validate_python(data)
    
    if len(restaurants) == 0:
        warnings.warn("This couldn't be tested correctly because there were no restaurants.")

def test_restaurants_endpoint_with_has_menu_query(client):
    response = client.get("/restaurants?hasMenu=true")
    assert response.status_code == 200, f"Failed! Server returned: {response.json()}"
    data = response.json()
    
    adapter = TypeAdapter(list[Restaurant])
    
    restaurants = adapter.validate_python(data)
    
    if len(restaurants) == 0:
        warnings.warn("This couldn't be tested correctly because there were no restaurants.")
