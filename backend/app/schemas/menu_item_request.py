from pydantic import BaseModel

from .offer import Offer
from .restricted_diet import RestrictedDiet

class MenuItemCreate(BaseModel):
    name: str
    description: str = ""
    suitableForDiet: RestrictedDiet | list[RestrictedDiet]
    offers: Offer | list[Offer]


class MenuItemUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    suitableForDiet: RestrictedDiet | list[RestrictedDiet] | None = None
    offers: Offer | list[Offer] | None = None

