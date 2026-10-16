import pytest
from pydantic import ValidationError
from backend.app.schemas.restaurant_request import RestaurantCreate

def valid_data():
    return {
        "name": "Pizza Palace",
        "address": "123 Main St",
        "telephone": "+1-250-555-0100",
        "openingHours": "Mo-Su 11:00-22:00",
    }

# Valid input

def test_valid_restaurant_is_accepted():
    restaurant = RestaurantCreate(**valid_data())

    assert restaurant.name == "Pizza Palace"
    assert restaurant.description == ""
    assert restaurant.address == "123 Main St"
    assert restaurant.telephone == "+1-250-555-0100"
    assert restaurant.openingHours == "Mo-Su 11:00-22:00"

def test_description_can_be_set():
    restaurant = RestaurantCreate(**{**valid_data(), "description": "Wood-fired pizza"})

    assert restaurant.description == "Wood-fired pizza"

def test_blank_description_is_allowed():
    restaurant = RestaurantCreate(**{**valid_data(), "description": "   "})

    assert restaurant.description == ""

def test_whitespace_is_stripped_from_all_fields():
    restaurant = RestaurantCreate(
        name="  Pizza Palace  ",
        description="  Wood-fired pizza  ",
        address="  123 Main St  ",
        telephone="  +1-250-555-0100  ",
        openingHours="  Mo-Su 11:00-22:00  ",
    )

    assert restaurant.name == "Pizza Palace"
    assert restaurant.description == "Wood-fired pizza"
    assert restaurant.address == "123 Main St"
    assert restaurant.telephone == "+1-250-555-0100"
    assert restaurant.openingHours == "Mo-Su 11:00-22:00"

# Missing required fields

def test_missing_name_is_rejected():
    data = valid_data()
    del data["name"]

    with pytest.raises(ValidationError):
        RestaurantCreate(**data)

def test_missing_address_is_rejected():
    data = valid_data()
    del data["address"]

    with pytest.raises(ValidationError):
        RestaurantCreate(**data)

def test_missing_telephone_is_rejected():
    data = valid_data()
    del data["telephone"]

    with pytest.raises(ValidationError):
        RestaurantCreate(**data)

def test_missing_opening_hours_is_rejected():
    data = valid_data()
    del data["openingHours"]

    with pytest.raises(ValidationError):
        RestaurantCreate(**data)

# Blank required fields

def test_blank_name_is_rejected():
    with pytest.raises(ValidationError):
        RestaurantCreate(**{**valid_data(), "name": "   "})

def test_blank_address_is_rejected():
    with pytest.raises(ValidationError):
        RestaurantCreate(**{**valid_data(), "address": "   "})

def test_blank_opening_hours_is_rejected():
    with pytest.raises(ValidationError):
        RestaurantCreate(**{**valid_data(), "openingHours": "   "})

# Maximum lengths

def test_name_of_100_characters_is_accepted():
    restaurant = RestaurantCreate(**{**valid_data(), "name": "a" * 100})

    assert restaurant.name == "a" * 100

def test_name_longer_than_100_characters_is_rejected():
    with pytest.raises(ValidationError):
        RestaurantCreate(**{**valid_data(), "name": "a" * 101})

def test_description_of_500_characters_is_accepted():
    restaurant = RestaurantCreate(**{**valid_data(), "description": "a" * 500})

    assert restaurant.description == "a" * 500

def test_description_longer_than_500_characters_is_rejected():
    with pytest.raises(ValidationError):
        RestaurantCreate(**{**valid_data(), "description": "a" * 501})

def test_address_of_200_characters_is_accepted():
    restaurant = RestaurantCreate(**{**valid_data(), "address": "a" * 200})

    assert restaurant.address == "a" * 200

def test_address_longer_than_200_characters_is_rejected():
    with pytest.raises(ValidationError):
        RestaurantCreate(**{**valid_data(), "address": "a" * 201})

def test_opening_hours_of_94_characters_is_accepted():
    hours = ", ".join(["Mo 09:00-17:00"] * 6)

    restaurant = RestaurantCreate(**{**valid_data(), "openingHours": hours})

    assert restaurant.openingHours == hours

def test_opening_hours_longer_than_100_characters_is_rejected():
    hours = ", ".join(["Mo 09:00-17:00"] * 7)

    with pytest.raises(ValidationError):
        RestaurantCreate(**{**valid_data(), "openingHours": hours})

# Fields the server controls

def test_client_cannot_set_id():
    with pytest.raises(ValidationError):
        RestaurantCreate(**{**valid_data(), "id": "abc123"})

# Opening hours format

def test_opening_hours_with_several_parts_is_accepted():
    restaurant = RestaurantCreate(**{**valid_data(), "openingHours": "Mo-Fr 09:00-17:00, Sa 10:00-14:00"})

    assert restaurant.openingHours == "Mo-Fr 09:00-17:00, Sa 10:00-14:00"

def test_opening_hours_with_list_of_days_is_accepted():
    restaurant = RestaurantCreate(**{**valid_data(), "openingHours": "Mo,We,Fr 09:00-17:00"})

    assert restaurant.openingHours == "Mo,We,Fr 09:00-17:00"

def test_opening_hours_closing_at_midnight_is_accepted():
    restaurant = RestaurantCreate(**{**valid_data(), "openingHours": "Mo-Su 05:00-00:00"})

    assert restaurant.openingHours == "Mo-Su 05:00-00:00"

def test_opening_hours_with_unknown_day_is_rejected():
    with pytest.raises(ValidationError):
        RestaurantCreate(**{**valid_data(), "openingHours": "Xy 09:00-17:00"})

def test_opening_hours_with_impossible_time_is_rejected():
    with pytest.raises(ValidationError):
        RestaurantCreate(**{**valid_data(), "openingHours": "Mo-Fr 24:00-17:00"})

def test_opening_hours_with_impossible_minutes_is_rejected():
    with pytest.raises(ValidationError):
        RestaurantCreate(**{**valid_data(), "openingHours": "Mo-Fr 09:60-17:00"})

def test_opening_hours_with_single_digit_hour_is_rejected():
    with pytest.raises(ValidationError):
        RestaurantCreate(**{**valid_data(), "openingHours": "Mo-Fr 9:00-17:00"})

def test_opening_hours_with_text_after_comma_is_rejected():
    with pytest.raises(ValidationError):
        RestaurantCreate(**{**valid_data(), "openingHours": "Mo-Fr 09:00-17:00, closed on holidays"})

def test_opening_hours_without_days_is_rejected():
    with pytest.raises(ValidationError):
        RestaurantCreate(**{**valid_data(), "openingHours": "09:00-17:00"})

# Telephone format

def test_telephone_with_letters_is_rejected():
    with pytest.raises(ValidationError):
        RestaurantCreate(**{**valid_data(), "telephone": "call me"})

def test_telephone_with_plus_in_middle_is_rejected():
    with pytest.raises(ValidationError):
        RestaurantCreate(**{**valid_data(), "telephone": "250+555+0100"})

def test_telephone_with_two_leading_plus_signs_is_rejected():
    with pytest.raises(ValidationError):
        RestaurantCreate(**{**valid_data(), "telephone": "++1-250-555-0100"})

def test_telephone_shorter_than_7_characters_is_rejected():
    with pytest.raises(ValidationError):
        RestaurantCreate(**{**valid_data(), "telephone": "123456"})

def test_telephone_of_7_characters_is_accepted():
    restaurant = RestaurantCreate(**{**valid_data(), "telephone": "1234567"})

    assert restaurant.telephone == "1234567"

def test_telephone_of_25_characters_is_accepted():
    restaurant = RestaurantCreate(**{**valid_data(), "telephone": "1" * 25})

    assert restaurant.telephone == "1" * 25

def test_telephone_longer_than_25_characters_is_rejected():
    with pytest.raises(ValidationError):
        RestaurantCreate(**{**valid_data(), "telephone": "1" * 26})

def test_international_telephone_is_accepted():
    restaurant = RestaurantCreate(**{**valid_data(), "telephone": "+44 20 7946 0958"})

    assert restaurant.telephone == "+44 20 7946 0958"

def test_telephone_with_dots_is_accepted():
    restaurant = RestaurantCreate(**{**valid_data(), "telephone": "250.555.0100"})

    assert restaurant.telephone == "250.555.0100"
