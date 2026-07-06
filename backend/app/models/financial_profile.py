from datetime import datetime
from decimal import Decimal
from sqlalchemy import ForeignKey, String, Numeric, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base

class FinancialProfile(Base):
    """Represents calculated financial ratios and stress index levels linked to a single user."""
    __tablename__ = "financial_profiles"

    profile_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), 
        unique=True, 
        nullable=False, 
        index=True
    )
    
    # Financial Ratios
    emi_ratio: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False, default=0.00) # EMI-to-Income percentage
    dti_ratio: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False, default=0.00) # Debt-to-Income percentage
    monthly_surplus: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False, default=0.00) # surplus cash flow
    stress_level: Mapped[str] = mapped_column(String(50), nullable=False, default="Low") # Low, Moderate, Severe, Critical
    
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now(), 
        onupdate=func.now(), 
        nullable=False
    )

    # Relationships
    user: Mapped["User"] = relationship(back_populates="financial_profile")

    def __repr__(self) -> str:
        return f"<FinancialProfile(profile_id={self.profile_id}, user_id={self.user_id}, stress_level='{self.stress_level}')>"
