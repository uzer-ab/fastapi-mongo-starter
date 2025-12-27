from beanie import Document, before_event, Insert, Replace
from pydantic import Field
from datetime import datetime, timezone
from typing import Optional
import uuid

class Session(Document):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str = Field(..., index=True)
    refresh_jti: str = Field(..., unique=True, index=True)  # Store as plain text
    device_info: Optional[str] = Field(max_length=255, default=None)
    ip_address: Optional[str] = Field(max_length=45, default=None)
    user_agent: Optional[str] = Field(max_length=500, default=None)
    expires_at: datetime = Field(..., index=True)
    is_active: bool = Field(default=True, index=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), index=True)
    last_activity: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), index=True)
    
    class Settings:
        name = "sessions"

    
    def is_expired(self) -> bool:
        return datetime.now(timezone.utc) > self.expires_at
    
    def is_valid(self) -> bool:
        return self.is_active and not self.is_expired()
    
    async def update_last_activity(self):
        self.last_activity = datetime.now(timezone.utc)
        await self.save()
    
    async def revoke(self):
        self.is_active = False
        await self.save()
    
    @classmethod
    async def find_by_jti(cls, jti: str) -> Optional["Session"]:
        return await cls.find_one(cls.refresh_jti == jti, cls.is_active == True)
    
    @classmethod
    async def find_valid_by_jti(cls, jti: str) -> Optional["Session"]:
        session = await cls.find_one(cls.refresh_jti == jti)
        
        if session and session.is_valid():
            return session
        
        return None
    
    @classmethod
    async def find_active_by_user(cls, user_id: str):
        return await cls.find(
            cls.user_id == user_id,
            cls.is_active == True
        ).to_list()
    
    @classmethod
    async def revoke_all_user_sessions(cls, user_id: str):
        await cls.find(cls.user_id == user_id).update({"$set": {"is_active": False}})
    
    @classmethod
    async def cleanup_expired_sessions(cls):
        current_time = datetime.now(timezone.utc)
        result = await cls.find(cls.expires_at < current_time).delete()
        return result.deleted_count