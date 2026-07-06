from typing import List, Optional
from decimal import Decimal
from sqlalchemy import String, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base, TimestampMixin

class User(Base, TimestampMixin):
    """Represents a platform user account containing login credentials and monthly budget figures."""
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    
    # Financial profile core metrics
    monthly_income: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False, default=0.00)
    monthly_expenses: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False, default=0.00)

    # Relationships
    # One-to-One: User <-> FinancialProfile
    financial_profile: Mapped[Optional["FinancialProfile"]] = relationship(
        back_populates="user", 
        cascade="all, delete-orphan", 
        uselist=False
    )
    
    # One-to-Many: User <-> Loans
    loans: Mapped[List["Loan"]] = relationship(
        back_populates="user", 
        cascade="all, delete-orphan"
    )
    
    # One-to-Many: User <-> AIHistories
    ai_histories: Mapped[List["AIHistory"]] = relationship(
        back_populates="user", 
        cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<User(id={self.id}, name='{self.name}', email='{self.email}')>"
