"""Settlement recommendation routes: AI-powered settlement analysis."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.loan import Loan
from app.models.user import User
from app.models.settlement import SettlementRecommendation
from app.schemas.settlement import SettlementCreate, SettlementResponse
from app.utils.auth import get_current_user
from app.services.ai_service import generate_settlement_recommendation

router = APIRouter(prefix="/api/settlements", tags=["Settlements"])


@router.post("/", response_model=SettlementResponse, status_code=status.HTTP_201_CREATED)
def generate_settlement(
    settlement_data: SettlementCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Generate an AI-powered settlement recommendation for a loan."""
    loan = db.query(Loan).filter(
        Loan.id == settlement_data.loan_id,
        Loan.user_id == current_user.id,
    ).first()
    if not loan:
        raise HTTPException(status_code=404, detail="Loan not found or not yours")

    # Calculate monthly surplus for AI analysis
    total_emi = db.query(Loan).filter(
        Loan.user_id == current_user.id, Loan.is_active == True
    ).with_entities(
        __import__('sqlalchemy').func.sum(Loan.monthly_emi)
    ).scalar() or 0

    surplus = (current_user.monthly_income or 0) - total_emi

    # Generate AI recommendation
    ai_result = generate_settlement_recommendation(
        lender_name=loan.lender_name,
        loan_type=loan.loan_type,
        outstanding_amount=loan.outstanding_amount,
        emi=loan.monthly_emi,
        interest_rate=loan.interest_rate or 0,
        overdue_months=loan.overdue_duration_months,
        monthly_income=current_user.monthly_income or 0,
        surplus=surplus,
    )

    # Save recommendation
    record = SettlementRecommendation(
        user_id=current_user.id,
        loan_id=loan.id,
        recommended_settlement_amount=ai_result["recommended_settlement_amount"],
        settlement_percentage=ai_result["settlement_percentage"],
        savings_amount=ai_result["savings_amount"],
        rationale=ai_result.get("rationale", ""),
        risk_factors=ai_result.get("risk_factors", []),
        ai_analysis=f"AI Analysis: {ai_result.get('rationale', 'No analysis available.')}",
        repayment_plan_months=ai_result.get("repayment_plan_months", 6),
        is_accepted=0,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


@router.get("/", response_model=List[SettlementResponse])
def get_settlements(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get all settlement recommendations for the user."""
    return db.query(SettlementRecommendation).filter(
        SettlementRecommendation.user_id == current_user.id
    ).order_by(SettlementRecommendation.created_at.desc()).all()


@router.get("/{settlement_id}", response_model=SettlementResponse)
def get_settlement(
    settlement_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a specific settlement recommendation."""
    record = db.query(SettlementRecommendation).filter(
        SettlementRecommendation.id == settlement_id,
        SettlementRecommendation.user_id == current_user.id,
    ).first()
    if not record:
        raise HTTPException(status_code=404, detail="Settlement recommendation not found")
    return record


@router.post("/{settlement_id}/accept")
def accept_settlement(
    settlement_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Mark a settlement recommendation as accepted."""
    record = db.query(SettlementRecommendation).filter(
        SettlementRecommendation.id == settlement_id,
        SettlementRecommendation.user_id == current_user.id,
    ).first()
    if not record:
        raise HTTPException(status_code=404, detail="Settlement recommendation not found")

    record.is_accepted = 1
    db.commit()
    return {"message": "Settlement accepted", "settlement_id": record.id}
