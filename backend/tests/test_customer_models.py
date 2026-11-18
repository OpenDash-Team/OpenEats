import pytest
from pydantic import ValidationError

from backend.app.schemas.customer_request import CustomerCreate, CustomerUpdate


def valid_customer(**changes):
    data = {"name": "Jordan Smith", "email": "jordan@example.com", "password": "password123"}
    return {**data, **changes}


def test_create_accepts_minimal_valid_customer():
    customer = CustomerCreate(**valid_customer())

    assert customer.telephone is None
    assert customer.address is None


def test_create_stores_email_in_lowercase():
    customer = CustomerCreate(**valid_customer(email="Jordan@Example.COM"))

    assert customer.email == "jordan@example.com"


def test_create_accepts_password_of_exactly_128_characters():
    customer = CustomerCreate(**valid_customer(password="a" * 128))

    assert len(customer.password) == 128


def test_create_keeps_spaces_in_password():
    customer = CustomerCreate(**valid_customer(password="  spaced out  "))

    assert customer.password == "  spaced out  "


@pytest.mark.parametrize("field, value", [
    ("email", "not-an-email"),
    ("password", "short"),
    ("password", "        "),
    ("password", "a" * 129),
    ("name", ""),
    ("telephone", "call me"),
])
def test_create_rejects_invalid_values(field, value):
    with pytest.raises(ValidationError):
        CustomerCreate(**valid_customer(**{field: value}))


@pytest.mark.parametrize("field", ["role", "isActive", "id", "hashedPassword"])
def test_create_rejects_fields_the_client_should_not_set(field):
    with pytest.raises(ValidationError):
        CustomerCreate(**valid_customer(**{field: "anything"}))


def test_update_needs_at_least_one_field():
    with pytest.raises(ValidationError):
        CustomerUpdate()


def test_update_rejects_password_change():
    with pytest.raises(ValidationError):
        CustomerUpdate(password="newpassword123")
