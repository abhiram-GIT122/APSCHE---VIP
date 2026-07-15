"""Loan management routes: CRUD operations for loans."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.loan import Loan
from app.models.user import User
from app.models.financial_profile import FinancialProfile
from app.schemas.loan import LoanCreate, LoanResponse, LoanUpdate
from app.schemas.financial import FinancialProfileResponse
from app.utils.auth import get_current_user
from app.services.financial_service import calculate_financial_metrics, update_financial_profile

router = APIRouter(prefix="/api/loans", tags=["Loans"])


@router.post("/", response_model=LoanResponse, status_code=status.HTTP_201_CREATED)
def create_loan(
    loan_data: LoanCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Add a new loan for the authenticated user."""
    loan = Loan(user_id=current_user.id, **loan_data.model_dump())
    db.add(loan)
    db.commit()
    db.refresh(loan)

    # Recalculate financial profile after adding loan
    metrics = calculate_financial_metrics(db, current_user)
    update_financial_profile(db, current_user, metrics)

    return loan


@router.get("/", response_model=List[LoanResponse])
def get_all_loans(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get all loans for the authenticated user."""
    loans = db.query(Loan).filter(Loan.user_id == current_user.id).all()
    return loans


@router.get("/{loan_id}", response_model=LoanResponse)
def get_loan(
    loan_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a specific loan by ID."""
    loan = db.query(Loan).filter(Loan.id == loan_id, Loan.user_id == current_user.id).first()
    if not loan:
        raise HTTPException(status_code=404, detail="Loan not found")
    return loan


@router.put("/{loan_id}", response_model=LoanResponse)
def update_loan(
    loan_id: int,
    updates: LoanUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update a specific loan."""
    loan = db.query(Loan).filter(Loan.id == loan_id, Loan.user_id == current_user.id).first()
    if not loan:
        raise HTTPException(status_code=404, detail="Loan not found")

    update_data = updates.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(loan, field, value)

    db.commit()
    db.refresh(loan)

    # Recalculate financial profile
    metrics = calculate_financial_metrics(db, current_user)
    update_financial_profile(db, current_user, metrics)

    return loan


@router.delete("/{loan_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_loan(
    loan_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a loan."""
    loan = db.query(Loan).filter(Loan.id == loan_id, Loan.user_id == current_user.id).first()
    if not loan:
        raise HTTPException(status_code=404, detail="Loan not found")

    db.delete(loan)
    db.commit()

    # Recalculate financial profile
    metrics = calculate_financial_metrics(db, current_user)
    update_financial_profile(db, current_user, metrics)
