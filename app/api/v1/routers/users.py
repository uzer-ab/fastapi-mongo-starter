from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
import logging
from app.schemas.user import User, UserCreate, UserUpdate
from app.models.user import User as UserModel
from app.models.role import Role
from app.dependencies import get_current_user
from app.services.session_service import SessionService
from app.utils.formatter import ApiResponse, ErrorResponse
from beanie.operators import Eq, Or


logger = logging.getLogger(__name__)


router = APIRouter(prefix="/user", tags=["user"])


@router.get("/", response_model=ApiResponse[User])
async def read_own_profile(current_user: UserModel = Depends(get_current_user)):
    logger.debug(f"Profile read by: {current_user.username} (role: {current_user.role.name})")
    return ApiResponse(code=0, message="success", data=current_user)


@router.put("/", response_model=ApiResponse[User])
async def update_own_profile(
    user_in: UserUpdate,
    current_user: UserModel = Depends(get_current_user)
):
    logger.info(
        f"Self-update by: {current_user.username}, "
        f"fields: {list(user_in.model_dump(exclude_unset=True).keys())}"
    )
    
    user = await UserModel.get(current_user.id)
    if not user or not user.is_active:
        logger.warning(f"User not found for update: ID={current_user.id}")
        raise HTTPException(status_code=404, detail="User not found")
    
    update_data = user_in.model_dump(exclude_unset=True)
    
    # Users cannot change their own role
    if "role" in update_data:
        logger.warning(f"User {current_user.username} attempted to change own role")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Cannot change your own role. Contact an administrator."
        )
    
    if "password" in update_data:
        logger.info(f"Password change by: {current_user.username}")
        update_data["password"] = update_data.pop("password")
    
    await user.set(update_data)
    await user.fetch_link("role")
    
    logger.info(f"User self-updated: {current_user.username} (ID: {user.id})")
    return ApiResponse(code=0, message="Profile updated successfully", data=user)


@router.delete("/", response_model=ApiResponse[None])
async def delete_own_account(current_user: UserModel = Depends(get_current_user)):
    logger.warning(f"Self-delete by: {current_user.username} (ID: {current_user.id})")
    
    user = await UserModel.get(current_user.id)
    if not user or not user.is_active:
        logger.warning(f"User not found for delete: ID={current_user.id}")
        raise HTTPException(status_code=404, detail="User not found")
    
    await user.set({"is_active": False})
    revoked_count = await SessionService.revoke_all_user_sessions(str(current_user.id))
    
    logger.info(
        f"User soft-deleted: {current_user.username} (ID: {current_user.id}), "
        f"{revoked_count} sessions revoked"
    )
    return ApiResponse(code=0, message="Account deleted successfully", data=None)
