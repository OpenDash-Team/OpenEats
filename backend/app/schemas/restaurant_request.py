from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, model_validator

# Opening hours in schema.org format, e.g. "Mo-Fr 09:00-17:00, Sa 10:00-14:00"
DAY = "(Mo|Tu|We|Th|Fr|Sa|Su)"
DAYS = f"{DAY}(-{DAY})?(,{DAY}(-{DAY})?)*"
TIME = "([01][0-9]|2[0-3]):[0-5][0-9]"
HOURS = f"{DAYS} {TIME}-{TIME}"
OPENING_HOURS_PATTERN = f"^{HOURS}(, {HOURS})*$"

# Field rules shared by the create and update models
Name = Annotated[str, Field(min_length=1, max_length=100)]
Description = Annotated[str, Field(max_length=500)]
Address = Annotated[str, Field(min_length=1, max_length=200)]
Telephone = Annotated[str, Field(pattern=r"^\+?[0-9 ().-]{7,25}$")]
OpeningHours = Annotated[str, Field(max_length=100, pattern=OPENING_HOURS_PATTERN)]

class RestaurantCreate(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    name: Name = Field(description="Restaurant name")
    description: Description = Field("", description="Short description of the restaurant")
    address: Address = Field(description="Street address")
    telephone: Telephone = Field(description="Phone number: digits, spaces, '+', '(', ')', '-', '.', 7-25 characters")
    openingHours: OpeningHours = Field(description="Opening hours in schema.org format, e.g. 'Mo-Fr 09:00-17:00, Sa 10:00-14:00'")

class RestaurantUpdate(BaseModel):
    """Only the fields that are sent get changed. A field left out or sent as null stays the same."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    name: Name | None = Field(None, description="New restaurant name")
    description: Description | None = Field(None, description="New description")
    address: Address | None = Field(None, description="New street address")
    telephone: Telephone | None = Field(None, description="New phone number: digits, spaces, '+', '(', ')', '-', '.', 7-25 characters")
    openingHours: OpeningHours | None = Field(None, description="New opening hours in schema.org format, e.g. 'Mo-Fr 09:00-17:00, Sa 10:00-14:00'")

    @model_validator(mode="after")
    def check_at_least_one_field(self):
        if all(value is None for value in self.model_dump().values()):
            raise ValueError("At least one field must be provided")
        return self
