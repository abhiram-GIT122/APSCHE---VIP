from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Any

from app.api.dependencies import get_db, get_current_user
from app.models.user import User
from app.schemas.ai_history import AIHistoryResponse
from app.schemas.response import StandardResponse
from app.services.ai_history import ai_history_service

router = APIRouter(prefix="/ai-history", tags=["AI History"])

@router.get("/", response_model=StandardResponse[List[AIHistoryResponse]])
async def get_history(
    page: int = Query(default=1, ge=1, description="Page number to retrieve"),
    size: int = Query(default=10, ge=1, le=100, description="Number of logs per page"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Retrieve paginated list of AI audit history logs for the authenticated user, ordered by newest first."""
    skip = (page - 1) * size
    res = await ai_history_service.get_history_by_user(db, current_user.id, skip=skip, limit=size)
    return {
        "success": True,
        "data": res,
        "message": "AI History logs retrieved successfully"
    }

@router.get("/{history_id}", response_model=StandardResponse[AIHistoryResponse])
async def get_history_item(
    history_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Retrieve details of a specific AI history log. Ownership is verified."""
    item = await ai_history_service.repo.get_by_id(db, history_id)
    if not item or item.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="History record not found."
        )
    return {
        "success": True,
        "data": item,
        "message": "AI History log item retrieved successfully"
    }

@router.delete("/{history_id}", response_model=StandardResponse[None])
async def delete_history_item(
    history_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Delete a single AI history log. Ownership is verified."""
    success = await ai_history_service.delete_history_item(db, history_id, current_user.id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="History record not found or could not be deleted."
        )
    return {
        "success": True,
        "data": None,
        "message": "AI History log item deleted successfully"
    }

@router.delete("/", response_model=StandardResponse[None])
async def clear_all_history(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Clear all AI history records belonging to the authenticated user."""
    await ai_history_service.clear_user_history(db, current_user.id)
    return {
        "success": True,
        "data": None,
        "message": "AI History logs cleared successfully"
    }
