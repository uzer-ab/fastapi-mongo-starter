from fastapi import APIRouter, Depends, HTTPException, status, Header, Request, Response, Cookie
from typing import List, Optional
import logging

from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from app.core.db import get_beanie_session
from app.dependencies import get_current_user
from app.models.role import Role
from app.models.session import Session
from app.models.user import User
from app.schemas.auth import (
    LoginRequest, TokenData, TokenRefreshResponse, TokenResponse, RefreshRequest, LogoutResponse
)
from app.schemas.user import UserCreate, UserResponse
from app.services.session_service import session_service
from app.core.config import get_settings
from app.utils.formatter import ApiResponse
from jose import jwt
from app.utils.auth import decode_jwt
from beanie.operators import Eq, Or, And

from app.utils.user_agent import get_client_ip


logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["auth"])
security = HTTPBearer(auto_error=True)


@router.post("/register", response_model=ApiResponse[UserResponse], status_code=201)
async def create_user(user_in: UserCreate):
    logger.info(f"Create user attempt: {user_in.username} ({user_in.email})")
    
    existing_user = await User.find_one(
        Or(
            Eq(User.username, user_in.username),
            Eq(User.email, user_in.email)
        )
    )
    
    if existing_user:
        logger.warning(f"User already exists: {user_in.username} or {user_in.email}")
        raise HTTPException(
            status_code=400,
            detail="Username or email already registered"
        )
    
    role = await Role.find_one(Role.name == user_in.role)
    if not role:
        raise HTTPException(status_code=400, detail=f"Role '{user_in.role}' not found")
    
    db_user = User(
        username=user_in.username,
        email=user_in.email,
        full_name=user_in.full_name,
        password=user_in.password,
        role=role
    )
    await db_user.insert()
    logger.info(f"User created: ID={db_user.id} ({db_user.username}, role={role.name})")

    user_dict = db_user.dict(exclude={"password"})
    return ApiResponse(code=0, message="User registered successfully", data=user_dict)


@router.post("/login", response_model=ApiResponse[TokenResponse])
async def login(
    form_data: LoginRequest,
    request: Request,
    response: Response,
    _: None = Depends(get_beanie_session)
):    
    client_ip = request.client.host
    logger.info(f"Login attempt: {form_data.email} from {client_ip}")
    
    login_identifier = form_data.email
    user = await User.find_one(
        And(
            Or(
                Eq(User.email, login_identifier),
                Eq(User.username, login_identifier)
            ),
            Eq(User.is_active, True)
        )
    )

    if not user:
        logger.warning(f"Login FAILED: User not found - {form_data.email} from {client_ip}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not await user.verify_and_rehash_password(form_data.password):
        logger.warning(f"Login FAILED: Invalid password - {form_data.email} from {client_ip}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    await user.fetch_link("role")

    token_response = await session_service.create_session(user, request, response)
    logger.info(f"Login SUCCESS: {user.username} (ID: {user.id}) from {client_ip}")
    return ApiResponse(code=0, message="Login successful", data=token_response)


@router.post("/refresh", response_model=ApiResponse[TokenRefreshResponse])
async def refresh_token(
    request: Request,
    current_user: User = Depends(get_current_user),
    refresh_token: Optional[str] = Cookie(None),
    _: None = Depends(get_beanie_session)
):
    client_ip = request.client.host
    logger.debug(f"Refresh token from {client_ip}, session: {refresh_token[:16]}...")

    token_data = await session_service.refresh_session(
        refresh_token,
        current_user,
        request
    )
    if not token_data:
        logger.warning(f"Refresh FAILED: Invalid/expired token from {client_ip}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return ApiResponse(code=0, message="Token refreshed successfully", data=token_data)


@router.post("/logout", response_model=ApiResponse[LogoutResponse])
async def logout(
    request: Request,
    response: Response,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    refresh_token: Optional[str] = Cookie(None),
    _: None = Depends(get_beanie_session)
):
    client_ip = get_client_ip(request)
    logger.info(f"Logout attempt from {client_ip}")
    
    session_id = None
    
    if credentials:
        try:
            token = credentials.credentials
            payload = decode_jwt(token)
            session_id = payload.get("sid")
            logger.debug(f"Session ID from access token: {session_id[:8] if session_id else 'None'}...")
        except jwt.JWTError as e:
            logger.debug(f"Could not decode access token: {str(e)}")
    
    if not session_id and refresh_token:
        try:
            payload = decode_jwt(refresh_token)
            session_id = payload.get("sid")
            logger.debug(f"Session ID from refresh token cookie: {session_id[:8] if session_id else 'None'}...")
        except jwt.JWTError as e:
            logger.debug(f"Could not decode refresh token: {str(e)}")
    
    if not session_id:
        logger.warning(f"Logout FAILED: No valid token provided from {client_ip}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Valid access token or refresh token required"
        )
    
    try:
        revoked = await session_service.revoke_session(session_id, response)
        
        if not revoked:
            logger.warning(f"Logout FAILED: Session not found {session_id[:8]}... from {client_ip}")
            # Still clear the cookie even if session not found
            session_service._clear_refresh_token_cookie(response)
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="Session not found"
            )
        
        logger.info(f"Logout SUCCESS: session={session_id[:8]}... from {client_ip}")
        
        logout_data = LogoutResponse(
            message="Logged out successfully", 
            revoked_sessions=1
        )
        
        return ApiResponse(
            code=0, 
            message="Logged out successfully", 
            data=logout_data
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Logout ERROR from {client_ip}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail="Logout failed"
        )
