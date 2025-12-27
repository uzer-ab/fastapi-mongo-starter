from fastapi.middleware.cors import CORSMiddleware
from app.middleware.http_logger import HTTPLoggerMiddleware

def setup_middleware(app):
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # TODO: Restrict in production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(HTTPLoggerMiddleware)
