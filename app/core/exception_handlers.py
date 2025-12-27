from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
import logging

logger = logging.getLogger(__name__)


async def http_exception_handler(request: Request, exc: HTTPException):
    logger.warning(
        f"HTTP {exc.status_code}: {exc.detail} - "
        f"Path: {request.url.path} - Method: {request.method}"
    )
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "code": exc.status_code,
            "message": exc.detail,
            "data": None
        }
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.warning(
        f"Validation error - Path: {request.url.path} - "
        f"Errors: {exc.errors()}"
    )
    return JSONResponse(
        status_code=422,
        content={
            "code": 422,
            "message": "Validation error",
            "details": exc.errors()
        }
    )


async def general_exception_handler(request: Request, exc: Exception):
    logger.error(
        f"Unhandled exception: {str(exc)} - "
        f"Path: {request.url.path} - Method: {request.method}",
        exc_info=True
    )
    return JSONResponse(
        status_code=500,
        content={
            "code": 500,
            "message": "Internal server error",
            "data": None
        }
    )


def setup_exception_handlers(app: FastAPI):
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(Exception, general_exception_handler)
