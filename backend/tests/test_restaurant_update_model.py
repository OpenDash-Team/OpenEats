import pytest
from pydantic import ValidationError
from backend.app.schemas.restaurant_request import RestaurantUpdate

# Valid input

def test_single_field_is_accepted():
    update = RestaurantUpdate(name="Pizza Palace")

    assert update.name == "Pizza Palace"
    assert update.description is None
    assert update.address is None
    assert update.telephone is None
    assert update.openingHours is None

def test_several_fields_are_accepted():
    update = RestaurantUpdate(telephone="+1-250-555-0199", openingHours="Mo-Fr 09:00-17:00, Sa 10:00-14:00")

    assert update.telephone == "+1-250-555-0199"
    assert update.openingHours == "Mo-Fr 09:00-17:00, Sa 10:00-14:00"

def test_description_can_be_cleared():
    update = RestaurantUpdate(description="")

    assert update.description == ""

def test_whitespace_is_stripped():
    update = RestaurantUpdate(name="  Pizza Palace  ")

    assert update.name == "Pizza Palace"

# Empty updates

def test_empty_update_is_rejected():
    with pytest.raises(ValidationError):
        RestaurantUpdate()

def test_update_with_only_nulls_is_rejected():
    with pytest.raises(ValidationError):
        RestaurantUpdate(name=None, address=None)

# Same rules as creating a restaurant

def test_blank_name_is_rejected():
    with pytest.raises(ValidationError):
        RestaurantUpdate(name="   ")

def test_name_longer_than_100_characters_is_rejected():
    with pytest.raises(ValidationError):
        RestaurantUpdate(name="a" * 101)

def test_description_longer_than_500_characters_is_rejected():
    with pytest.raises(ValidationError):
        RestaurantUpdate(description="a" * 501)

def test_blank_address_is_rejected():
    with pytest.raises(ValidationError):
        RestaurantUpdate(address="   ")

def test_address_longer_than_200_characters_is_rejected():
    with pytest.raises(ValidationError):
        RestaurantUpdate(address="a" * 201)

def test_invalid_telephone_is_rejected():
    with pytest.raises(ValidationError):
        RestaurantUpdate(telephone="call me")

def test_invalid_opening_hours_is_rejected():
    with pytest.raises(ValidationError):
        RestaurantUpdate(openingHours="Mo-Fr 99:00-17:00")

def test_opening_hours_longer_than_100_characters_is_rejected():
    with pytest.raises(ValidationError):
        RestaurantUpdate(openingHours=", ".join(["Mo 09:00-17:00"] * 7))

# Fields the server controls

def test_client_cannot_change_id():
    with pytest.raises(ValidationError):
        RestaurantUpdate(name="Pizza Palace", id="abc123")

def test_client_cannot_change_menu():
    with pytest.raises(ValidationError):
        RestaurantUpdate(name="Pizza Palace", hasMenu={})
