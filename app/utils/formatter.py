from typing import TypeVar, Generic, Optional
from pydantic import BaseModel, Field

T = TypeVar('T')

class ApiResponse(BaseModel, Generic[T]):
    code: int = Field(default=0, description="0 for success, non-zero for errors")
    message: str = Field(default="success", description="Response message")
    data: Optional[T] = None

class ErrorResponse(BaseModel):
    code: int
    message: str
    details: Optional[dict] = None