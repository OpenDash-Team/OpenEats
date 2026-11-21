from pydantic import BaseModel, ConfigDict, Field

from .cart import Quantity


class CartItemAdd(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    menuItemId: str = Field(min_length=1, description="Id of the menu item to add")
    quantity: Quantity = Field(1, description="How many to add, 1-99. Adding an item already in the cart increases its quantity")


class CartItemUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    quantity: Quantity = Field(description="New quantity, 1-99. To remove an item use DELETE instead")
