"""Loan model to store individual loan details."""
from sqlalchemy import Column, Integer, Float, String, DateTime, ForeignKey, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class Loan(Base):
    __tablename__ = "loans"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    lender_name = Column(String(100), nullable=False)
    loan_type = Column(String(50), nullable=False)  # personal, home, education, credit_card, etc.
    outstanding_amount = Column(Float, nullable=False)
    original_amount = Column(Float, nullable=True)
    monthly_emi = Column(Float, nullable=False)
    interest_rate = Column(Float, nullable=True)  # annual %
    overdue_duration_months = Column(Integer, default=0)
    tenure_months = Column(Integer, nullable=True)
    remaining_months = Column(Integer, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    user = relationship("User", back_populates="loans")
