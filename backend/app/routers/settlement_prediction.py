from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Any
from pydantic import BaseModel, Field

from app.api.dependencies import get_db, get_current_user
from app.models.user import User
from app.schemas.settlement_prediction import SettlementPredictionResponse
from app.schemas.response import StandardResponse
from app.services.settlement_service import settlement_prediction_service
from app.services.loan import loan_service

router = APIRouter(prefix="/settlement-prediction", tags=["Settlement Prediction"])

class PredictionGenerateRequest(BaseModel):
    """Input payload to trigger a settlement prediction for a loan."""
    loan_id: int = Field(..., description="ID of the loan to analyze")

@router.post("/generate", response_model=StandardResponse[SettlementPredictionResponse])
async def generate_prediction(
    request_in: PredictionGenerateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Generates an AI settlement proposal prediction for a user's loan."""
    # Verify loan ownership
    loan = await loan_service.get_loan_by_id(db, request_in.loan_id)
    if not loan or loan.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Loan record not found."
        )

    result = await settlement_prediction_service.predict_settlement(db, request_in.loan_id)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate settlement prediction."
        )
        
    prediction, explanation = result
    # Temporarily attach explanation parameter for API Pydantic serialization
    prediction.explanation = explanation
    return {
        "success": True,
        "data": prediction,
        "message": "Settlement prediction generated successfully"
    }

@router.get("/history", response_model=StandardResponse[List[SettlementPredictionResponse]])
async def get_prediction_history(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Retrieve the historical settlement predictions for all loans belonging to the current user."""
    predictions = await settlement_prediction_service.get_predictions_by_user(db, current_user.id)
    return {
        "success": True,
        "data": predictions,
        "message": "Prediction history retrieved successfully"
    }

@router.get("/{prediction_id}", response_model=StandardResponse[SettlementPredictionResponse])
async def get_prediction(
    prediction_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Retrieve details of a specific settlement prediction. Ownership is verified."""
    prediction = await settlement_prediction_service.repo.get_by_id(db, prediction_id)
    if not prediction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Settlement prediction not found."
        )
        
    # Verify ownership via loan relations
    loan = await loan_service.get_loan_by_id(db, prediction.loan_id)
    if not loan or loan.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Settlement prediction not found."
        )
        
    return {
        "success": True,
        "data": prediction,
        "message": "Settlement prediction retrieved successfully"
    }
