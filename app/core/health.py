from fastapi import Request, HTTPException
from app.core.db import get_database
from app.core.config import get_settings
from datetime import datetime, timezone

settings = get_settings()

async def health_check():
    return {
        "status": "healthy",
        "version": settings.VERSION,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

async def readiness_check():
    try:
        db = await get_database()
        await db.command("ping")
        return {"status": "ready"}
    except Exception:
        raise HTTPException(status_code=503, detail="Database not ready")

def setup_health_endpoints(app):
    app.get("/health")(health_check)
    app.get("/ready")(readiness_check)
    @app.get("/", tags=["root"])
    def root(request: Request):
        return {
            "message": settings.PROJECT_NAME,
            "version": settings.VERSION,
            "docs": "/docs",
            "redoc": "/redoc",
            "health": "/health",
            "ready": "/ready",
            "client_ip": request.client.host,
        }