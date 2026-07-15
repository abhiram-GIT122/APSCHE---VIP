from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, Dict, List , Any


class SettlementCreate(BaseModel):
    loan_id: int = Field(..., description="ID of the loan to analyze for settlement")


class SettlementResponse(BaseModel):
    id: int
    user_id: int
    loan_id: int
    recommended_settlement_amount: float
    settlement_percentage: float
    savings_amount: float
    rationale: Optional[str] = None
    risk_factors: Optional[list[str, Any]] = None
    ai_analysis: Optional[str] = None
    repayment_plan_months: Optional[int] = None
    is_accepted: int
    created_at: Optional[datetime] = None

    model_config = {"from_attributes": True}
