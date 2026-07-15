"""Financial profile model for aggregated user financial health data."""
from sqlalchemy import Column, Integer, Float, String, DateTime, ForeignKey, JSON
from sqlalchemy.sql import func
from app.database import Base


class FinancialProfile(Base):
    __tablename__ = "financial_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    total_debt = Column(Float, default=0.0)
    total_emi = Column(Float, default=0.0)
    emi_to_income_ratio = Column(Float, default=0.0)  # percentage
    monthly_surplus = Column(Float, default=0.0)
    debt_stress_level = Column(String(20), default="LOW")  # LOW, MODERATE, HIGH, CRITICAL
    credit_score_estimate = Column(Integer, nullable=True)
    settlement_readiness_score = Column(Float, nullable=True)
    ai_insights = Column(JSON, nullable=True)  # AI-generated insights as JSON
    last_updated = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
