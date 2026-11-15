from pydantic import BaseModel, Field

from ..core.identifiers import generate_id

from .menu_section import MenuSection

class Menu(BaseModel):
    type: str = Field("Menu", frozen=True)
    id: str = Field(default_factory=generate_id, frozen=True)
    hasMenuSection: MenuSection | list[MenuSection]