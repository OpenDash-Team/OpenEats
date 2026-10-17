from pydantic import BaseModel, ConfigDict, model_validator, Field
from .offer import Offer
from .restricted_diet import RestrictedDiet

class MenuItemCreate(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    name: str = Field(min_length=1)
    description: str = ""
    suitableForDiet: RestrictedDiet | list[RestrictedDiet]
    offers: Offer | list[Offer]


class MenuItemUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    name: str | None = Field(None, min_length=1)
    description: str | None = None
    suitableForDiet: RestrictedDiet | list[RestrictedDiet] | None = None
    offers: Offer | list[Offer] | None = None

    @model_validator(mode="after")
    def check_at_least_one_field(self):
        if all(value is None for value in self.model_dump().values()):
            raise ValueError("At least one field must be provided")
        return self