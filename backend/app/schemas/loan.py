from datetime import datetime
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict

class LoanBase(BaseModel):
    """Shared base properties for Loan validations."""
    lender_name: str = Field(..., min_length=1, max_length=150, description="Name of the lending institution")
    loan_type: str = Field(default="Personal", min_length=1, max_length=100, description="Type of loan")
    principal_amount: Decimal = Field(default=Decimal("0.00"), ge=0, description="Principal loan amount")
    outstanding_amount: Decimal = Field(..., ge=0, description="Remaining balance owed")
    interest_rate: Decimal = Field(..., ge=0, le=100, description="Annual percentage interest rate")
    emi_amount: Decimal = Field(default=Decimal("0.00"), ge=0, description="Equated Monthly Installment value")
    tenure_months: int = Field(default=0, ge=0, description="Total tenure of the loan in months")
    overdue_months: int = Field(default=0, ge=0, description="Number of months payments are past due")
    status: str = Field(default="active", description="Status of the loan (active, closed)")

    # Legacy emi field alias support to prevent breaking other dependencies
    @property
    def emi(self) -> Decimal:
        return self.emi_amount

class LoanCreate(LoanBase):
    """Schema for validating loan creation inputs."""
    pass

class LoanUpdate(BaseModel):
    """Schema for validating loan updates. All fields are optional."""
    lender_name: Optional[str] = Field(None, min_length=1, max_length=150)
    loan_type: Optional[str] = Field(None, min_length=1, max_length=100)
    principal_amount: Optional[Decimal] = Field(None, ge=0)
    outstanding_amount: Optional[Decimal] = Field(None, ge=0)
    interest_rate: Optional[Decimal] = Field(None, ge=0, le=100)
    emi_amount: Optional[Decimal] = Field(None, ge=0)
    tenure_months: Optional[int] = Field(None, ge=0)
    overdue_months: Optional[int] = Field(None, ge=0)
    status: Optional[str] = Field(None)

class LoanResponse(LoanBase):
    """Schema for serializing loan details in API responses."""
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
        # Allow accessing attributes by legacy names if needed
        populate_by_name=True
    )
