from beanie import Document
from pydantic import Field
from datetime import datetime, timezone
from typing import List, Optional
import uuid


class Role(Document):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    
    name: str = Field(..., max_length=50, unique=True)
    description: Optional[str] = Field(max_length=255, default=None)
    permissions: List[str] = Field(default_factory=list)
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    class Settings:
        name = "roles"
