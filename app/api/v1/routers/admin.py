from fastapi import APIRouter, Depends, HTTPException, Query, status
from typing import List
import logging
from app.models.user import User as UserModel
from app.models.role import Role
from app.schemas.admin import ListUsers
from app.schemas.user import User, UserResponse, UserUpdate
from app.dependencies import require_admin, require_permission
from app.utils.formatter import ApiResponse
from beanie.operators import Eq, And

from app.services.session_service import SessionService


logger = logging.getLogger(__name__)

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/users", response_model=ApiResponse[ListUsers])
async def list_all_users(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(10, ge=1, le=100, description="Items per page"),
    current_user: UserModel = Depends(require_admin)
):
    logger.info(f"List all users requested by: {current_user.username} (page: {page}, page_size: {size})")
    
    skip = (page - 1) * size
    
    total_count = await UserModel.find_all().count()
    
    users = await UserModel.find_all().skip(skip).limit(size).to_list()
    
    users_data = []
    for user in users:
        await user.fetch_link("role")
        users_data.append({
            "id": str(user.id),
            "username": user.username,
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role,
            "is_active": user.is_active,
            "created_at": user.created_at
        })
    
    total_pages = (total_count + size - 1) // size
    has_next = page < total_pages
    has_previous = page > 1
    
    logger.info(f"Returned {len(users_data)} users to {current_user.username} (page {page}/{total_pages})")
    
    return ApiResponse(
        code=0,
        message=f"Retrieved {len(users_data)} users successfully",
        data={
            "users": users_data,
            "pagination": {
                "total_items": total_count,
                "total_pages": total_pages,
                "current_page": page,
                "page_size": size,
                "has_next": has_next,
                "has_previous": has_previous
            }
        }
    )


@router.put("/{user_id}", response_model=ApiResponse[User])
async def update_any_user(
    user_id: str,
    user_in: UserUpdate,
    current_user: UserModel = Depends(require_admin)
):
    logger.info(
        f"Admin {current_user.username} updating user {user_id}, "
        f"fields: {list(user_in.model_dump(exclude_unset=True).keys())}"
    )
    
    # Prevent admin from editing themselves
    if str(user_id) == str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Use PUT /user/ to update your own profile"
        )
    
    user = await UserModel.get(user_id)
    if not user:
        logger.warning(f"User not found for update: ID={user_id}")
        raise HTTPException(status_code=404, detail="User not found")
    
    update_data = user_in.model_dump(exclude_unset=True)
    
    # Check if admin is trying to change role
    if "role" in update_data:        
        role = await Role.find_one(Role.name == update_data["role"])
        if not role:
            raise HTTPException(status_code=400, detail="Role not found")
        update_data["role"] = role
    
    if "password" in update_data:
        logger.info(f"Admin {current_user.username} changing password for {user.username}")
        update_data["password"] = update_data.pop("password")
    
    await user.set(update_data)
    await user.fetch_link("role")
    
    logger.info(
        f"User {user.username} updated by admin {current_user.username} (ID: {user.id})"
    )
    return ApiResponse(
        code=0, 
        message="User updated successfully", 
        data=user
    )


@router.delete("/{user_id}", response_model=ApiResponse[None])
async def delete_any_user(
    user_id: str,
    current_user: UserModel = Depends(require_admin)
):
    logger.warning(
        f"Admin {current_user.username} deleting user: {user_id}"
    )
    
    # Prevent admin from deleting themselves
    if str(user_id) == str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Use DELETE /user/ to delete your own account"
        )
    
    user = await UserModel.get(user_id)
    if not user:
        logger.warning(f"User not found for delete: ID={user_id}")
        raise HTTPException(status_code=404, detail="User not found")
    
    if not user.is_active:
        raise HTTPException(status_code=400, detail="User already deactivated")
    
    await user.set({"is_active": False})
    revoked_count = await SessionService.revoke_all_user_sessions(str(user.id))
    
    logger.info(
        f"User {user.username} soft-deleted by admin {current_user.username}, "
        f"{revoked_count} sessions revoked"
    )
    return ApiResponse(
        code=0, 
        message=f"User deleted successfully, {revoked_count} sessions revoked", 
        data=None
    )
