from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Any

from app.api.dependencies import get_db, get_current_user
from app.models.user import User
from app.schemas.user import UserResponse, UserUpdate
from app.schemas.response import StandardResponse
from app.services.user import user_service

router = APIRouter(prefix="/users", tags=["Users"])

@router.get("/me", response_model=StandardResponse[UserResponse])
async def get_me(current_user: User = Depends(get_current_user)) -> Any:
    """Retrieve profile metrics and details for the currently authenticated user."""
    return {
        "success": True,
        "data": current_user,
        "message": "User profile retrieved successfully"
    }

@router.put("/me", response_model=StandardResponse[UserResponse])
async def update_me(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Update profile parameters of the currently authenticated user."""
    updated_user = await user_service.update_user(db, current_user.id, user_update)
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User account not found"
        )
    return {
        "success": True,
        "data": updated_user,
        "message": "User profile updated successfully"
    }

@router.delete("/me", response_model=StandardResponse[None])
async def delete_me(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Delete the account of the currently authenticated user."""
    success = await user_service.repo.delete(db, current_user)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while deleting the user account"
        )
    return {
        "success": True,
        "data": None,
        "message": "User account deleted successfully"
    }
