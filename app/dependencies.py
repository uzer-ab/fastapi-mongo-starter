from fastapi import Depends, HTTPException, status, Request, Cookie
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from typing import List, Optional
import logging

from app.core.db import get_beanie_session
from app.models.user import User
from app.models.session import Session
from app.services.session_service import session_service
from app.core.config import get_settings
from app.utils.auth import decode_jwt
from beanie.operators import Eq

logger = logging.getLogger(__name__)
security = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    refresh_token: Optional[str] = Cookie(None),
    _: None = Depends(get_beanie_session)
) -> User:
    token = None
    token_source = None
    
    if credentials:
        token = credentials.credentials
        token_source = "access_token"
        logger.debug(f"Using Bearer token: {credentials.scheme} {token[:10]}...")
    elif refresh_token:
        token = refresh_token
        token_source = "refresh_token"
        logger.debug(f"Using refresh token from cookie: {token[:10]}...")
    else:
        logger.debug("No authentication token provided")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated. Provide Bearer token or refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    try:
        payload = decode_jwt(token)
        
        token_type = payload.get("type")
        
        if token_source == "access_token" and token_type != "access":
            logger.warning(f"Invalid token type in Bearer: {token_type}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type. Access token required",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        if token_source == "refresh_token" and token_type != "refresh":
            logger.warning(f"Invalid token type in cookie: {token_type}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token",
                headers={"WWW-Authenticate": "Bearer"},
            )
            
    except jwt.ExpiredSignatureError:
        logger.warning(f"Token expired (source: {token_source})")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired. Please login again",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.InvalidTokenError as e:
        logger.warning(f"Invalid token (source: {token_source}): {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        logger.error(f"JWT decode error (source: {token_source}): {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token validation failed",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user_id: Optional[str] = payload.get("uid")
    session_id: Optional[str] = payload.get("sid")

    if not user_id or not session_id:
        logger.warning(f"Missing claims: uid={user_id}, sid={session_id}, source={token_source}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token claims",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    logger.debug(f"Token claims (source: {token_source}): uid={user_id}, sid={session_id[:8]}...")
    
    db_session = await session_service.validate_session(session_id)
    if not db_session:
        logger.warning(f"Session invalid: {session_id[:8]}... (source: {token_source})")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session expired or revoked. Please login again",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if db_session.user_id != user_id:
        logger.warning(
            f"Session/User mismatch: session.user_id={db_session.user_id}, "
            f"token.user_id={user_id}, source={token_source}"
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Session not authorized for this user"
        )
    
    try:
        user = await User.get(user_id)
        
        if not user:
            logger.warning(f"User not found: {user_id} (source: {token_source})")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        if not user.is_active:
            logger.warning(f"Inactive user attempted access: {user_id} (source: {token_source})")
            await session_service.revoke_all_user_sessions(user_id)
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is disabled"
            )
        
        await user.fetch_link(User.role)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"User lookup error for {user_id}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve user information"
        )
    
    logger.info(
        f"Auth OK: {user.username} "
        f"({user.role.name if user.role else 'no role'}, ID: {user.id[:8]}...) "
        f"via {token_source}"
    )
    return user

def require_permission(required_permissions: List[str]):
    async def permission_checker(
        current_user: User = Depends(get_current_user)
    ) -> User:
        user_permissions = current_user.role.permissions
        
        if not has_permission(user_permissions, required_permissions):
            logger.warning(
                f"Permission denied for {current_user.username}: "
                f"required {required_permissions}"
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )
        
        logger.debug(
            f"Permission granted to {current_user.username}: {required_permissions}"
        )
        return current_user
    
    return permission_checker


def has_permission(user_permissions: List[str], required: List[str]) -> bool:
    if "*" in user_permissions:
        return True
    
    # Check each required permission
    for req in required:
        if req in user_permissions:
            continue
        
        # Check namespace wildcards (e.g., "admin:*" matches "admin:read")
        namespace = req.split(":")[0] if ":" in req else None
        if namespace and f"{namespace}:*" in user_permissions:
            continue
        
        return False
    
    return True

require_user = require_permission(["user:*"])
require_admin = require_permission(["admin:*"])
require_super_admin = require_permission(["*"])
