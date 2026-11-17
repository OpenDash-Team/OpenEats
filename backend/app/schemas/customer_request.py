from typing import Annotated

from pydantic import BaseModel, ConfigDict, EmailStr, Field, StringConstraints, field_validator, model_validator

from .restaurant_request import Address, Name, Telephone

# Passwords are kept exactly as typed (no space stripping), otherwise login would not match
Password = Annotated[str, StringConstraints(strip_whitespace=False, min_length=8, max_length=128)]


def normalize_email(email: str | None) -> str | None:
    # Emails are compared case-insensitively, so they are always stored in lowercase
    return email.lower() if email is not None else None


class CustomerCreate(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    name: Name = Field(description="Customer's full name")
    email: EmailStr = Field(description="Email address, used to sign in. Must not already be registered")
    password: Password = Field(description="Password, 8-128 characters")
    telephone: Telephone | None = Field(None, description="Phone number: digits, spaces, '+', '(', ')', '-', '.', 7-25 characters")
    address: Address | None = Field(None, description="Delivery address")

    _lowercase_email = field_validator("email")(normalize_email)

    @field_validator("password")
    @classmethod
    def check_password_not_blank(cls, password: str) -> str:
        if not password.strip():
            raise ValueError("Password can't be only spaces")
        return password


class CustomerUpdate(BaseModel):
    """Only the fields that are sent get changed. A field left out or sent as null stays the same."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    name: Name | None = Field(None, description="New name")
    email: EmailStr | None = Field(None, description="New email address. Must not belong to another customer")
    telephone: Telephone | None = Field(None, description="New phone number")
    address: Address | None = Field(None, description="New delivery address")

    _lowercase_email = field_validator("email")(normalize_email)

    @model_validator(mode="after")
    def check_at_least_one_field(self):
        if all(value is None for value in self.model_dump().values()):
            raise ValueError("At least one field must be provided")
        return self
