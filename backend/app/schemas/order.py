from datetime import datetime, timezone
from decimal import Decimal
from typing import Literal
from pydantic import BaseModel, Field
from ..core.identifiers import generate_id


class OrderItem(BaseModel):
    menuItemId: str
    name: str = Field(min_length=1)
    quantity: int = Field(strict=True, ge=1, le=99)
    unitPrice: Decimal = Field(ge=0) # to calculate money value precisely
    lineTotal: Decimal = Field(ge=0)


class Order(BaseModel):
    id: str = Field(default_factory=generate_id, frozen=True)
    customerId: str
    restaurantId: str
    cartId: str
    items: list[OrderItem] = Field(min_length=1)
    currency: str = Field(min_length=3, max_length=3)
    subtotal: Decimal = Field(ge=0)
    total: Decimal = Field(ge=0)
    deliveryAddress: str = Field(min_length=1)
    createdAt: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    status: Literal["created"] = "created"