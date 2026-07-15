"""Settlement recommendation model for AI-generated settlement suggestions."""
from sqlalchemy import Column, Integer, Float, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.sql import func
from app.database import Base


class SettlementRecommendation(Base):
    __tablename__ = "settlement_recommendations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    loan_id = Column(Integer, ForeignKey("loans.id"), nullable=False)
    recommended_settlement_amount = Column(Float, nullable=False)
    settlement_percentage = Column(Float, nullable=False)
    savings_amount = Column(Float, nullable=False)
    rationale = Column(Text, nullable=True)
    risk_factors = Column(JSON, nullable=True)
    ai_analysis = Column(Text, nullable=True)
    repayment_plan_months = Column(Integer, nullable=True)
    is_accepted = Column(Integer, default=0)  # 0=pending, 1=accepted, 2=rejected
    created_at = Column(DateTime(timezone=True), server_default=func.now())
