from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Any

from app.api.dependencies import get_db, get_current_user
from app.models.user import User
from app.schemas.ai_negotiation import AINegotiationCreate, AINegotiationResponse
from app.schemas.response import StandardResponse
from app.services.ai_negotiation_service import ai_negotiation_service
from app.services.loan import loan_service

router = APIRouter(prefix="/ai-negotiation", tags=["AI Negotiation"])

@router.post("/generate", response_model=StandardResponse[AINegotiationResponse])
async def generate_negotiation_letter(
    request_in: AINegotiationCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Generates an AI hardship and payout proposal letter for a user's delinquent loan."""
    # Verify loan ownership
    loan = await loan_service.get_loan_by_id(db, request_in.loan_id)
    if not loan or loan.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Loan record not found."
        )

    negotiation = await ai_negotiation_service.generate_negotiation_letter(db, current_user.id, request_in)
    if not negotiation:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate negotiation letter."
        )
        
    return {
        "success": True,
        "data": negotiation,
        "message": "AI Negotiation letter generated successfully"
    }

@router.get("/history", response_model=StandardResponse[List[AINegotiationResponse]])
async def get_negotiation_history(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Retrieve all historical negotiation letters generated for the current user."""
    negotiations = await ai_negotiation_service.get_negotiations_by_user(db, current_user.id)
    return {
        "success": True,
        "data": negotiations,
        "message": "Negotiation history retrieved successfully"
    }

@router.get("/{negotiation_id}", response_model=StandardResponse[AINegotiationResponse])
async def get_negotiation(
    negotiation_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Retrieve details of a specific negotiation letter. Ownership is verified."""
    negotiation = await ai_negotiation_service.repo.get_by_id(db, negotiation_id)
    if not negotiation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Negotiation letter not found."
        )
        
    # Verify ownership via loan relations
    loan = await loan_service.get_loan_by_id(db, negotiation.loan_id)
    if not loan or loan.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Negotiation letter not found."
        )
        
    return {
        "success": True,
        "data": negotiation,
        "message": "Negotiation letter retrieved successfully"
    }
