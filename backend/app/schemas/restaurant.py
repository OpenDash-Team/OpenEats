from .menu import Menu

from pydantic import BaseModel, Field

from backend.app.core.identifiers import generate_id

class Restaurant(BaseModel):
    type: str = Field("Restaurant", frozen=True, )
    id: str = Field(default_factory=generate_id, frozen=True)
    name: str
    description: str = ""
    address: str
    telephone: str
    openingHours: str
    hasMenu: Menu | None = None