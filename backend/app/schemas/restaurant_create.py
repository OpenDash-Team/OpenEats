from pydantic import BaseModel, ConfigDict, Field

# Opening hours in schema.org format, e.g. "Mo-Fr 09:00-17:00, Sa 10:00-14:00"
DAY = "(Mo|Tu|We|Th|Fr|Sa|Su)"
DAYS = f"{DAY}(-{DAY})?(,{DAY}(-{DAY})?)*"
TIME = "([01][0-9]|2[0-3]):[0-5][0-9]"
HOURS = f"{DAYS} {TIME}-{TIME}"
OPENING_HOURS_PATTERN = f"^{HOURS}(, {HOURS})*$"

class RestaurantCreate(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    name: str = Field(min_length=1, max_length=100, description="Restaurant name")
    description: str = Field("", max_length=500, description="Short description of the restaurant")
    address: str = Field(min_length=1, max_length=200, description="Street address")
    telephone: str = Field(pattern=r"^\+?[0-9 ().-]{7,25}$", description="Phone number: digits, spaces, '+', '(', ')', '-', '.', 7-25 characters")
    openingHours: str = Field(max_length=100, pattern=OPENING_HOURS_PATTERN, description="Opening hours in schema.org format, e.g. 'Mo-Fr 09:00-17:00, Sa 10:00-14:00'")
