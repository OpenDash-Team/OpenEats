from typing import Optional
from fastapi import Query, Depends

class RestaurantQuery:
    def __init__(
        self,
        name: Optional[str] = Query(default=None, description="Filter by restaurant name"),
        hasMenu: Optional[bool] = Query(default=None, description="Filter by menu availability"),
        sort_by: Optional[str] = Query(default=None, description="Field to sort by (e.g., 'name')"),
        sort_desc: bool = Query(default=False, description="Sort in descending order")
    ):
        self.name = name
        self.hasMenu = hasMenu
        self.sort_by = sort_by
        self.sort_desc = sort_desc