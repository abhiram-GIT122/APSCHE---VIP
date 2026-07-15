"""Negotiation routes: generate negotiation letters using AI."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.loan import Loan
from app.models.user import User
from app.models.negotiation import NegotiationHistory
from app.schemas.negotiation import NegotiationCreate, NegotiationResponse
from app.utils.auth import get_current_user
from app.services.ai_service import generate_negotiation_letter

router = APIRouter(prefix="/api/negotiations", tags=["Negotiations"])


@router.post("/", response_model=NegotiationResponse, status_code=status.HTTP_201_CREATED)
def create_negotiation(
    negotiation_data: NegotiationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Generate an AI-powered negotiation letter for a loan."""
    # Verify loan belongs to user
    loan = db.query(Loan).filter(
        Loan.id == negotiation_data.loan_id,
        Loan.user_id == current_user.id,
    ).first()
    if not loan:
        raise HTTPException(status_code=404, detail="Loan not found or not yours")

    # Calculate proposed settlement if not provided
    proposed_settlement = negotiation_data.proposed_settlement_amount
    if not proposed_settlement:
        proposed_settlement = loan.outstanding_amount * 0.55  # Default 55% settlement

    settlement_pct = (proposed_settlement / loan.outstanding_amount * 100)

    # Generate AI negotiation letter
    ai_letter = generate_negotiation_letter(
        borrower_name=current_user.full_name or current_user.username,
        monthly_income=current_user.monthly_income or 0,
        total_debt=loan.outstanding_amount,
        loan_type=loan.loan_type,
        outstanding_amount=loan.outstanding_amount,
        overdue_months=loan.overdue_duration_months,
        emi=loan.monthly_emi,
        negotiation_type=negotiation_data.negotiation_type,
        proposed_settlement=proposed_settlement,
    )

    # Save negotiation record
    record = NegotiationHistory(
        user_id=current_user.id,
        loan_id=loan.id,
        lender_name=negotiation_data.lender_name,
        negotiation_type=negotiation_data.negotiation_type,
        proposed_settlement_amount=proposed_settlement,
        settlement_percentage=round(settlement_pct, 2),
        ai_generated_letter=ai_letter,
        notes=negotiation_data.notes,
        status="DRAFT",
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


@router.get("/", response_model=List[NegotiationResponse])
def get_negotiations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get all negotiation records for the user."""
    return db.query(NegotiationHistory).filter(
        NegotiationHistory.user_id == current_user.id
    ).order_by(NegotiationHistory.created_at.desc()).all()


@router.get("/{negotiation_id}", response_model=NegotiationResponse)
def get_negotiation(
    negotiation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a specific negotiation record."""
    record = db.query(NegotiationHistory).filter(
        NegotiationHistory.id == negotiation_id,
        NegotiationHistory.user_id == current_user.id,
    ).first()
    if not record:
        raise HTTPException(status_code=404, detail="Negotiation record not found")
    return record


@router.put("/{negotiation_id}/status")
def update_negotiation_status(
    negotiation_id: int,
    status_update: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update the status of a negotiation (DRAFT/SENT/ACCEPTED/REJECTED)."""
    record = db.query(NegotiationHistory).filter(
        NegotiationHistory.id == negotiation_id,
        NegotiationHistory.user_id == current_user.id,
    ).first()
    if not record:
        raise HTTPException(status_code=404, detail="Negotiation record not found")

    new_status = status_update.get("status")
    if new_status not in ["DRAFT", "SENT", "ACCEPTED", "REJECTED"]:
        raise HTTPException(status_code=400, detail="Invalid status")

    record.status = new_status
    db.commit()
    db.refresh(record)
    return {"message": "Status updated", "negotiation": record}
