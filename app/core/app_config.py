# main.py
from contextlib import asynccontextmanager
from fastapi import FastAPI
import logging
from datetime import datetime, timezone

from app.core.config import get_settings
from app.core.db import init_beanie_models, create_default_roles
from app.core.middleware import setup_middleware
from app.core.exception_handlers import setup_exception_handlers
from app.core.health import setup_health_endpoints
from app.api.v1 import routers
from app.utils.logging import setup_logging

# Initialize logging
setup_logging()

log = logging.getLogger("app")


@asynccontextmanager
async def lifespan(app_: FastAPI):
    log.info("🚀 Starting up...")
    await init_beanie_models()
    await create_default_roles()
    log.info("MongoDB collections initialized")
    yield
    log.info("🔌 Shutdown complete")


settings = get_settings()
app = FastAPI(title=settings.PROJECT_NAME, version=settings.VERSION, lifespan=lifespan)


# Setup core components
setup_middleware(app)
setup_exception_handlers(app)
setup_health_endpoints(app)


# Include routers
app.include_router(routers.users.router, prefix="/api/v1", tags=["user"])
app.include_router(routers.auth.router, prefix="/api/v1", tags=["auth"])
app.include_router(routers.admin.router, prefix="/api/v1", tags=["admin"])
