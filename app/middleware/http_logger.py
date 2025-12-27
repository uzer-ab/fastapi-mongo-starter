"""Log ALL requests in app.log."""
from fastapi import Request
import logging
import time
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Callable

log = logging.getLogger("app.http")

class HTTPLoggerMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable):
        start_time = time.time()
        client_ip = request.client.host
        
        log.info(f"← {client_ip} {request.method} {request.url.path} ({request.url.query})")
        
        response = await call_next(request)
        duration = (time.time() - start_time) * 1000
        
        log.info(f"→ {client_ip} {request.method} {request.url.path} {response.status_code} "
                f"{duration:.0f}ms")
        
        return response
