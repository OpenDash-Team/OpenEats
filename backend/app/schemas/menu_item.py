from pydantic import BaseModel, Field

from ..core.identifiers import generate_id

from .restricted_diet import RestrictedDiet
from .offer import Offer

class MenuItem(BaseModel):
    type: str = Field("MenuItem", frozen=True)
    id: str = Field(default_factory=generate_id, frozen=True)
    name: str
    description: str = ""
    suitableForDiet: RestrictedDiet | list[RestrictedDiet]
    offers: Offer | list[Offer]