from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime
from app.models.role import Role

class UserBase(BaseModel):
    username: str
    email: EmailStr
    full_name: Optional[str]
    role: Optional[str] = Field("USER")

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    password: Optional[str] = None
    role: Optional[str] = Field(None)
    is_active: Optional[bool] = None

class UserResponse(UserBase):
    id: str
    is_active: bool
    created_at: datetime
    role: Role

class User(UserBase):
    id: str
    role: Role
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True
