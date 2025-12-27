from beanie import Document, Link, before_event, Insert, Replace
from pydantic import Field
from datetime import datetime, timezone
from typing import Optional
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from .role import Role
import uuid

ph = PasswordHasher()

class User(Document):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    
    username: str = Field(..., max_length=50, unique=True, index=True)
    email: str = Field(..., max_length=100, unique=True, index=True)
    full_name: Optional[str] = Field(max_length=100, default=None)
    password: str = Field(..., max_length=255)
    role: Link[Role] = Field(...)
    is_active: bool = Field(default=True, index=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    class Settings:
        name = "users"
    
    @before_event(Insert, Replace)
    async def hash_password(self):
        if self.password:
            self.password = ph.hash(self.password)
    
    def verify_password(self, plain_password: str) -> bool:
        try:
            ph.verify(self.password, plain_password)
            return True
        except VerifyMismatchError:
            return False
    
    async def verify_and_rehash_password(self, plain_password: str) -> bool:
        try:
            ph.verify(self.password, plain_password)
            
            if ph.check_needs_rehash(self.password):
                print(f"Rehashing password for user {self.username}")
                self.password = ph.hash(plain_password)
                await self.save()
            
            return True
        except VerifyMismatchError:
            return False
    
    async def deactivate(self):
        self.is_active = False
        await self.save()
    
    @classmethod
    async def find_by_email(cls, email: str) -> Optional["User"]:
        return await cls.find_one(cls.email == email)
    
    @classmethod
    async def get_active_users(cls):
        return await cls.find(cls.is_active == True).to_list()