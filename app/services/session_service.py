from datetime import datetime, timedelta, timezone
from typing import Optional, List, Dict
import uuid
import logging
from fastapi import Request, Response, HTTPException, status

from app.utils.auth import generate_jwt
from app.utils.user_agent import parse_user_agent, get_client_ip
from app.core.config import get_settings
from app.models.user import User
from app.utils.auth import decode_jwt
from app.models.session import Session

logger = logging.getLogger(__name__)
settings = get_settings()

ACCESS_TOKEN_EXPIRE_MINUTES = 15
REFRESH_TOKEN_EXPIRE_DAYS = 30
SESSION_EXPIRE_HOURS = 24 * REFRESH_TOKEN_EXPIRE_DAYS  # Match refresh token expiry


class SessionService:
    @staticmethod
    async def create_session(
        user: User, 
        request: Request, 
        response: Response
    ) -> Dict[str, str]:

        session_id = str(uuid.uuid4())
        refresh_jti = str(uuid.uuid4())
        expires_at = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        
        access_token = SessionService._create_access_token(
            {
                "uid": str(user.id),
                "sid": session_id,
                "type": "access"
            },
            timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        )

        refresh_token = SessionService._create_access_token(
            {
                "uid": str(user.id),
                "sid": session_id,
                "jti": refresh_jti,
                "type": "refresh"
            },
            timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        )
        
        device_info = parse_user_agent(request)
        ip_address = get_client_ip(request)
        
        db_session = Session(
            id=session_id,
            user_id=str(user.id),
            refresh_jti=refresh_jti,
            device_info=device_info,
            ip_address=ip_address,
            user_agent=request.headers.get("User-Agent"),
            expires_at=expires_at,
            is_active=True
        )
        await db_session.insert()
        
        # Set refresh token in httpOnly cookie
        SessionService._set_refresh_token_cookie(response, refresh_token)
        
        logger.info(
            f"Session created: user={user.username}, "
            f"session={session_id[:8]}..., ip={ip_address}"
        )
        
        return {
            "token": {
                "access_token": access_token,
                "token_type": "bearer",
                "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            },
            "user": {
                "id": str(user.id),
                "username": user.username,
                "email": user.email,
                "full_name": user.full_name,
                "role": user.role,
                "is_active": user.is_active,
                "created_at": user.created_at
            }
        }
    
    @staticmethod
    async def validate_session(session_id: str) -> Optional[Session]:
        try:
            session = await Session.get(session_id)
            
            if session and session.is_valid():
                await session.update_last_activity()
                logger.debug(f"Session validated: {session_id[:8]}...")
                return session
            else:
                logger.debug(f"Session invalid or expired: {session_id[:8]}...")
                return None
            
        except Exception as e:
            logger.error(f"Session validation error for {session_id[:8]}...: {e}")
            return None
    
    @staticmethod
    async def refresh_session(
        refresh_token: str, 
        current_user: User,
        request: Request,
    ) -> Optional[Dict[str, str]]:
        try:
            
            payload = decode_jwt(refresh_token)
            if not payload or payload.get("type") != "refresh":
                logger.warning(f"Invalid refresh token type from {get_client_ip(request)}")
                return None
            
            jti = payload.get("jti")
            user_id = payload.get("uid")
            session_id = payload.get("sid")
            
            if not all([jti, user_id, session_id]):
                logger.warning(f"Missing required fields in refresh token")
                return None
            
            session = await Session.find_valid_by_jti(jti)
            
            if not session:
                logger.warning(f"Invalid or expired session refresh attempt from {get_client_ip(request)}")
                return None
            
            if session.id != session_id or session.user_id != user_id or user_id != current_user.id:
                logger.warning(f"Session mismatch in refresh token")
                await session.revoke()
                return None
            
            if not current_user.is_active:
                logger.warning(f"Refresh token for inactive/deleted user: {user_id}")
                await session.revoke()
                return None
            
            await session.update_last_activity()
            
            new_access_token = SessionService._create_access_token(
                {
                    "uid": str(current_user.id),
                    "sid": session.id,
                    "type": "access"
                },
                timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
            )
            
            logger.info(f"Session refreshed: user={current_user.username}, session={session.id[:8]}...")
            
            return {
                "token":{
                    "access_token": new_access_token,
                    "token_type": "bearer",
                    "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60
                }
            }
            
        except Exception as e:
            logger.error(f"Session refresh error: {e}")
            return None
    
    @staticmethod
    async def revoke_session(session_id: str, response: Response) -> bool:
        try:
            session = await Session.get(session_id)
            
            if session and session.is_active:
                await session.revoke()
                SessionService._clear_refresh_token_cookie(response)
                logger.info(f"Session revoked: {session_id[:8]}...")
                return True
            
            logger.debug(f"Session not found or already revoked: {session_id[:8]}...")
            return False
            
        except Exception as e:
            logger.error(f"Session revocation error for {session_id[:8]}...: {e}")
            return False
    
    @staticmethod
    async def revoke_all_user_sessions(user_id: str) -> int:
        try:
            sessions = await Session.find_active_by_user(user_id)
            count = len(sessions)
            
            if count > 0:
                await Session.revoke_all_user_sessions(user_id)
                logger.info(f"Revoked {count} sessions for user: {user_id}")
            
            return count
            
        except Exception as e:
            logger.error(f"Error revoking sessions for user {user_id}: {e}")
            return 0
    
    @staticmethod
    async def get_user_sessions(user_id: str) -> List[Session]:
        try:
            sessions = await Session.find_active_by_user(user_id)
            
            sessions.sort(key=lambda s: s.last_activity, reverse=True)
            
            logger.debug(f"Found {len(sessions)} active sessions for user: {user_id}")
            return sessions
            
        except Exception as e:
            logger.error(f"Error fetching sessions for user {user_id}: {e}")
            return []
    
    @staticmethod
    async def cleanup_expired_sessions() -> int:
        try:
            deleted_count = await Session.cleanup_expired_sessions()
            if deleted_count > 0:
                logger.info(f"Cleaned up {deleted_count} expired sessions")
            return deleted_count
        except Exception as e:
            logger.error(f"Error cleaning up expired sessions: {e}")
            return 0
    
    @staticmethod
    def _create_access_token(
        data: dict, 
        expires_delta: Optional[timedelta] = None
    ) -> str:
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({"exp": expire})
        
        return generate_jwt(to_encode)
    
    @staticmethod
    def _set_refresh_token_cookie(response: Response, refresh_token: str) -> None:
        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            httponly=True,
            secure=settings.ENVIRONMENT == "production",
            samesite="lax",
            max_age=REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,  # seconds
            path="/",
        )
        logger.debug("Refresh token set in httpOnly cookie")
    
    @staticmethod
    def _clear_refresh_token_cookie(response: Response) -> None:
        response.delete_cookie(
            key="refresh_token",
            path="/",
            httponly=True,
            secure=settings.ENVIRONMENT == "production",
            samesite="lax"
        )
        logger.debug("Refresh token cookie cleared")


session_service = SessionService()