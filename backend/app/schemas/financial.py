from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Dict, Any


class FinancialProfileResponse(BaseModel):
    id: int
    user_id: int
    total_debt: float
    total_emi: float
    emi_to_income_ratio: float
    monthly_surplus: float
    debt_stress_level: str
    credit_score_estimate: Optional[int] = None
    settlement_readiness_score: Optional[float] = None
    ai_insights: Optional[Dict[str, Any]] = None
    last_updated: Optional[datetime] = None

    model_config = {"from_attributes": True}


class FinancialAnalysis(BaseModel):
    total_debt: float
    total_emi: float
    emi_to_income_ratio: float
    monthly_surplus: float
    debt_stress_level: str
    risk_factors: list
    recommendations: list
    ai_summary: str
