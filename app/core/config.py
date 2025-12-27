from pydantic_settings import BaseSettings
from functools import lru_cache
import os

class Settings(BaseSettings):
    PROJECT_NAME: str = "FastAPI Scalable"
    VERSION: str = "0.1.0"
    
    MONGO_URL: str
    MONGODB_NAME: str
    
    SECRET_KEY: str = os.urandom(32).hex()
    ALGORITHM: str = "HS256"
    
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    WORKERS: int = int(os.cpu_count() * 1.4)
    ENVIRONMENT: str = "devlopment"
    
    class Config:
        env_file = ".env"

@lru_cache()
def get_settings() -> Settings:
    return Settings()
