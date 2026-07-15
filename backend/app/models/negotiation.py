"""Negotiation history model to track AI-generated negotiation letters."""
from sqlalchemy import Column, Integer, Float, String, Text, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.database import Base


class NegotiationHistory(Base):
    __tablename__ = "negotiation_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    loan_id = Column(Integer, ForeignKey("loans.id"), nullable=True)
    lender_name = Column(String(100), nullable=False)
    negotiation_type = Column(String(50), nullable=False)  # settlement, restructuring, waiver
    proposed_settlement_amount = Column(Float, nullable=True)
    settlement_percentage = Column(Float, nullable=True)
    ai_generated_letter = Column(Text, nullable=True)
    status = Column(String(30), default="DRAFT")  # DRAFT, SENT, ACCEPTED, REJECTED
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
