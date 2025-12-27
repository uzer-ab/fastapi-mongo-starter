from typing import AsyncGenerator
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from contextlib import asynccontextmanager
from app.core.config import get_settings
from app.models.user import User
from app.models.role import Role
from app.models.session import Session
import pytz

settings = get_settings()

_client: AsyncIOMotorClient = None

async def init_beanie_models():
    global _client
    if _client is None:
        _client = AsyncIOMotorClient(
            settings.MONGO_URL,
            tz_aware=True,
            tzinfo=pytz.UTC
            )
    
    await init_beanie(
        database=_client[settings.MONGODB_NAME],
        document_models=[Role, User, Session]
    )

async def get_database():
    global _client
    if _client is None:
        _client = AsyncIOMotorClient(settings.MONGO_URL)

    return _client[settings.MONGODB_NAME]

@asynccontextmanager
async def get_db_client() -> AsyncGenerator[AsyncIOMotorClient, None]:
    global _client
    if _client is None:
        _client = AsyncIOMotorClient(settings.MONGO_URL)
    
    try:
        yield _client
    finally:
        pass

async def get_beanie_session() -> AsyncGenerator[None, None]:
    yield

async def create_default_roles():
    roles = [
        Role(
            name="USER",
            description="Regular user with self-service capabilities",
            permissions=[
                "user:*"
            ]
        ),
        Role(
            name="ADMIN",
            description="Administrator with full system access",
            permissions=["admin:*"]
        ),
        Role(
            name="SUPER_ADMIN",
            description="Administrator with full system access",
            permissions=["*"]
        ),
    ]
    for role in roles:
        if not await Role.find_one(Role.name == role.name):
            await role.insert()