from __future__ import annotations

from pydantic import BaseModel, Field

from backend.app.core.identifiers import generate_id

from .menu_item import MenuItem

class MenuSection(BaseModel):
    type: str = Field("MenuSection", frozen=True)
    id: str = Field(default_factory=generate_id, frozen=True)
    name: str
    description: str = ""
    hasMenuSection: MenuSection | list[MenuSection] | None = None
    hasMenuItem: MenuItem | list[MenuItem] | None = None