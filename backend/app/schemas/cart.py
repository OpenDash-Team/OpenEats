from decimal import Decimal
from typing import Annotated, Literal

from pydantic import BaseModel, Field

from ..core.identifiers import generate_id

MAX_QUANTITY = 99

CartStatus = Literal["active", "checkedOut"]
Quantity = Annotated[int, Field(strict=True, ge=1, le=MAX_QUANTITY)]  # strict: "2" or true are rejected


class CartItem(BaseModel):
    """Only the item id is stored, so prices always come from the current menu."""

    menuItemId: str
    quantity: Quantity


class Cart(BaseModel):
    """A cart as it is stored in carts.json."""

    id: str = Field(default_factory=generate_id, frozen=True)
    customerId: str
    restaurantId: str | None = None  # a cart only holds items from one restaurant
    items: list[CartItem] = []
    status: CartStatus = "active"


class CartItemResponse(BaseModel):
    menuItemId: str
    name: str | None = Field(description="None if the item is no longer on the menu")
    quantity: int
    unitPrice: Decimal | None = Field(description="Current price, None if the item can't be ordered right now")
    lineTotal: Decimal
    available: bool = Field(description="False if the item is out of stock or no longer on the menu. It is left out of the totals")


class CartResponse(BaseModel):
    id: str
    customerId: str
    restaurantId: str | None
    items: list[CartItemResponse]
    currency: str | None
    subtotal: Decimal
    total: Decimal
