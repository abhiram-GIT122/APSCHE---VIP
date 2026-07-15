from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class NegotiationCreate(BaseModel):
    loan_id: int
    lender_name: str
    negotiation_type: str = Field(..., description="settlement, restructuring, waiver")
    proposed_settlement_amount: Optional[float] = Field(None, gt=0)
    notes: Optional[str] = None


class NegotiationResponse(BaseModel):
    id: int
    user_id: int
    loan_id: Optional[int] = None
    lender_name: str
    negotiation_type: str
    proposed_settlement_amount: Optional[float] = None
    settlement_percentage: Optional[float] = None
    ai_generated_letter: Optional[str] = None
    status: str
    notes: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}
