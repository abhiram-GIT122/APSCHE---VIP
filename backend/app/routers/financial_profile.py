from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Any

from app.api.dependencies import get_db, get_current_user
from app.models.user import User
from app.schemas.financial_profile import FinancialProfileResponse
from app.schemas.response import StandardResponse
from app.services.financial_profile_service import financial_profile_service

router = APIRouter(prefix="/financial-profile", tags=["Financial Profile"])

@router.get("/", response_model=StandardResponse[FinancialProfileResponse])
async def get_financial_profile(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Retrieve the financial profile for the current user, recalculated dynamically using the Financial Health Engine."""
    # Recalculate parameters dynamically using current budget and active loan obligations
    profile = await financial_profile_service.recalculate_profile(db, current_user.id)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Financial profile not found for this user."
        )
    return {
        "success": True,
        "data": profile,
        "message": "Financial profile retrieved successfully"
    }

@router.post("/calculate", response_model=StandardResponse[FinancialProfileResponse])
async def calculate_financial_profile(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Triggers recalculation of the user's financial ratios based on current monthly budget and active loans.
    
    Stress level calculations:
    - DTI < 0.3 -> Low (LOW)
    - 0.3 <= DTI <= 0.5 -> Medium (MEDIUM)
    - DTI > 0.5 -> High (HIGH)
    
    Surplus formula:
    - Monthly Surplus = Monthly Income - Monthly Expenses
    
    Saves and returns the updated profile.
    """
    profile = await financial_profile_service.recalculate_profile(db, current_user.id)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to compute financial profile metrics."
        )
    return {
        "success": True,
        "data": profile,
        "message": "Financial profile calculated successfully"
    }
