from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class LoanCreate(BaseModel):
    lender_name: str = Field(..., min_length=1, max_length=100)
    loan_type: str = Field(..., description="personal, home, education, credit_card, vehicle, business")
    outstanding_amount: float = Field(..., gt=0)
    original_amount: Optional[float] = Field(None, gt=0)
    monthly_emi: float = Field(..., gt=0)
    interest_rate: Optional[float] = Field(None, ge=0, le=100)
    overdue_duration_months: int = Field(0, ge=0)
    tenure_months: Optional[int] = Field(None, gt=0)
    remaining_months: Optional[int] = Field(None, ge=0)


class LoanUpdate(BaseModel):
    lender_name: Optional[str] = Field(None, min_length=1, max_length=100)
    outstanding_amount: Optional[float] = Field(None, gt=0)
    monthly_emi: Optional[float] = Field(None, gt=0)
    overdue_duration_months: Optional[int] = Field(None, ge=0)
    is_active: Optional[bool] = None


class LoanResponse(BaseModel):
    id: int
    user_id: int
    lender_name: str
    loan_type: str
    outstanding_amount: float
    original_amount: Optional[float] = None
    monthly_emi: float
    interest_rate: Optional[float] = None
    overdue_duration_months: int
    tenure_months: Optional[int] = None
    remaining_months: Optional[int] = None
    is_active: bool
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}
