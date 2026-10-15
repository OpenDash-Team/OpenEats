from pydantic import BaseModel, ConfigDict, Field

class RestaurantCreate(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    name: str = Field(min_length=1, description="Restaurant name")
    description: str = Field("", description="Short description of the restaurant")
    address: str = Field(min_length=1, description="Street address")
    telephone: str = Field(pattern=r"^\+?[0-9 ().-]{7,25}$", description="Phone number: digits, spaces, '+', '(', ')', '-', '.', 7-25 characters")
    openingHours: str = Field(min_length=1, description="Opening hours in schema.org format")
