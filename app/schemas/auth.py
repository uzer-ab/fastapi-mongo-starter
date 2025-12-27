from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime

from app.schemas.user import UserResponse

class LoginRequest(BaseModel):
    email: str
    password: str

class TokenData(BaseModel):
    access_token: str
    expires_in: int
    token_type: str = "bearer"

class TokenRefreshResponse(BaseModel):
    token: TokenData

class TokenResponse(BaseModel):
    token: TokenData
    user: UserResponse

class RefreshRequest(BaseModel):
    refresh_token: str

class LogoutResponse(BaseModel):
    revoked_sessions: int = 1
