from datetime import datetime
from decimal import Decimal
from sqlalchemy import ForeignKey, String, Numeric, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base

class Settlement(Base):
    """Stores AI generated settlement terms, target discount thresholds, and risk analysis metrics."""
    __tablename__ = "settlements"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    loan_id: Mapped[int] = mapped_column(
        ForeignKey("loans.id", ondelete="CASCADE"), 
        nullable=False, 
        index=True
    )
    
    suggested_settlement_percentage: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False) # target payout ratio e.g., 40.00%
    risk_score: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False, default=0.00) # numerical risk assessment score
    risk_category: Mapped[str] = mapped_column(String(50), nullable=False) # Low, Medium, High risk of lawsuit/rejection
    final_offer_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False) # absolute dollar target
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now(), 
        nullable=False
    )

    # Relationships
    loan: Mapped["Loan"] = relationship(back_populates="settlements")

    def __repr__(self) -> str:
        return f"<Settlement(id={self.id}, loan_id={self.loan_id}, risk_category='{self.risk_category}')>"
