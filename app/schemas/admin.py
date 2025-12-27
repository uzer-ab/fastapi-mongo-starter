from pydantic import BaseModel
from typing import List, Optional

from app.schemas.user import UserResponse

class Pagination(BaseModel):
    total_items: int
    total_pages: int
    current_page: int
    page_size: int
    has_next: bool
    has_previous: bool

class ListUsers(BaseModel):
    pagination: Pagination
    users: List[UserResponse]