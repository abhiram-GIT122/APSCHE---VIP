from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Any

from app.api.dependencies import get_db, get_current_user
from app.models.user import User
from app.schemas.loan import LoanCreate, LoanUpdate, LoanResponse
from app.schemas.response import StandardResponse
from app.services.loan import loan_service

router = APIRouter(prefix="/loans", tags=["Loans"])

@router.post("/", response_model=StandardResponse[LoanResponse], status_code=status.HTTP_201_CREATED)
async def create_loan(
    loan_in: LoanCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Register a new outstanding loan liability."""
    res = await loan_service.create_loan(db, current_user.id, loan_in)
    return {
        "success": True,
        "data": res,
        "message": "Loan record created successfully"
    }

@router.get("/", response_model=StandardResponse[List[LoanResponse]])
async def list_loans(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Retrieve all outstanding loan records owned by the authenticated user."""
    res = await loan_service.get_loans_by_user(db, current_user.id)
    return {
        "success": True,
        "data": res,
        "message": "Loans retrieved successfully"
    }

@router.get("/{loan_id}", response_model=StandardResponse[LoanResponse])
async def get_loan(
    loan_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Retrieve details of a specific loan. Ownership is verified."""
    loan = await loan_service.get_loan_by_id(db, loan_id)
    if not loan or loan.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Loan record not found"
        )
    return {
        "success": True,
        "data": loan,
        "message": "Loan record retrieved successfully"
    }

@router.put("/{loan_id}", response_model=StandardResponse[LoanResponse])
async def update_loan(
    loan_id: int,
    loan_update: LoanUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Update details of an existing loan. Ownership is verified."""
    loan = await loan_service.get_loan_by_id(db, loan_id)
    if not loan or loan.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Loan record not found"
        )
    
    updated_loan = await loan_service.update_loan(db, loan_id, loan_update)
    return {
        "success": True,
        "data": updated_loan,
        "message": "Loan record updated successfully"
    }

@router.delete("/{loan_id}", response_model=StandardResponse[None])
async def delete_loan(
    loan_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Remove a loan record from the platform. Ownership is verified."""
    loan = await loan_service.get_loan_by_id(db, loan_id)
    if not loan or loan.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Loan record not found"
        )
        
    await loan_service.delete_loan(db, loan_id)
    return {
        "success": True,
        "data": None,
        "message": "Loan record deleted successfully"
    }
