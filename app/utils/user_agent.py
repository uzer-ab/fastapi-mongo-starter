from user_agents import parse
from fastapi import Request
import logging

logger = logging.getLogger(__name__)


def parse_user_agent(request: Request) -> str:
    user_agent_str = request.headers.get("User-Agent", "Unknown")
    
    try:
        ua = parse(user_agent_str)
        parts = []
        
        # Browser
        if ua.browser.family:
            parts.append(ua.browser.family)
            if ua.browser.version_string:
                parts.append(ua.browser.version_string)
        
        # Operating System
        if ua.os.family:
            parts.append(ua.os.family)
            if ua.os.version_string:
                parts.append(ua.os.version_string)
        
        # Device
        if ua.device.family and ua.device.family != "Other":
            parts.append(ua.device.family)
        
        device_info = " | ".join(parts) if parts else "Unknown"
        logger.debug(f"Parsed UA: {device_info}")
        return device_info
        
    except Exception as e:
        logger.warning(f"Failed to parse user agent: {e}")
        return user_agent_str


def get_client_ip(request: Request) -> str:
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip
    
    return getattr(request.client, "host", "unknown")
