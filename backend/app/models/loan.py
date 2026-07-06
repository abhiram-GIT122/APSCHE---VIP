from typing import List
from decimal import Decimal
from sqlalchemy import ForeignKey, String, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base, TimestampMixin

class Loan(Base, TimestampMixin):
    """Represents a specific outstanding debt liability owned by a user."""
    __tablename__ = "loans"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), 
        nullable=False, 
        index=True
    )
    
    lender_name: Mapped[str] = mapped_column(String(150), nullable=False, index=True)
    loan_type: Mapped[str] = mapped_column(String(100), nullable=False, default="Personal") 
    principal_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False, default=0.00)
    outstanding_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False, default=0.00)
    interest_rate: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False, default=0.00)
    emi_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False, default=0.00)
    tenure_months: Mapped[int] = mapped_column(nullable=False, default=0)
    overdue_months: Mapped[int] = mapped_column(nullable=False, default=0)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="active") # active, closed

    # Relationships
    user: Mapped["User"] = relationship(back_populates="loans")
    
    settlements: Mapped[List["Settlement"]] = relationship(
        back_populates="loan", 
        cascade="all, delete-orphan"
    )
    
    ai_negotiations: Mapped[List["AINegotiation"]] = relationship(
        back_populates="loan", 
        cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Loan(id={self.id}, user_id={self.user_id}, lender_name='{self.lender_name}', outstanding_amount={self.outstanding_amount})>"
