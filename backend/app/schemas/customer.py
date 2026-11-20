from typing import Literal

from pydantic import BaseModel, Field

from ..core.identifiers import generate_id

CustomerRole = Literal["customer", "owner"]


class Customer(BaseModel):
    """A customer as it is stored in customers.json (includes the password hash)."""

    id: str = Field(default_factory=generate_id, frozen=True)
    name: str
    email: str
    hashedPassword: str
    tokenVersion: int = 0
    telephone: str | None = None
    address: str | None = None
    role: CustomerRole = "customer"
    isActive: bool = True


class CustomerResponse(BaseModel):
    """What the API sends back about a customer. Never includes the password hash."""

    id: str
    name: str
    email: str
    telephone: str | None = None
    address: str | None = None
    role: CustomerRole
    isActive: bool
