from jose import jwt
from app.core.config import get_settings

settings = get_settings()

SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM

def decode_jwt(data):
    return jwt.decode(data, SECRET_KEY, algorithms=[ALGORITHM])

def generate_jwt(data):
    return jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)