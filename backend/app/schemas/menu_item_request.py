from pydantic import BaseModel, ConfigDict, model_validator
from .offer import Offer
from .restricted_diet import RestrictedDiet

class MenuItemCreate(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    name: str
    description: str = ""
    suitableForDiet: RestrictedDiet | list[RestrictedDiet]
    offers: Offer | list[Offer]


class MenuItemUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    name: str | None = None
    description: str | None = None
    suitableForDiet: RestrictedDiet | list[RestrictedDiet] | None = None
    offers: Offer | list[Offer] | None = None

    @model_validator(mode="after")
    def check_at_least_one_field(self):
        if all(value is None for value in self.model_dump().values()):
            raise ValueError("At least one field must be provided")
        return self