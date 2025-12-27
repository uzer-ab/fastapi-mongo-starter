from app.core.app_config import app
from app.core.db import init_beanie_models, create_default_roles

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True, log_level="info")
