from datetime import datetime
from sqlalchemy import ForeignKey, String, Text, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base

class AINegotiation(Base):
    """Represents a generated AI settlement strategy draft and custom legal-tone hardship letter."""
    __tablename__ = "ai_negotiations"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    loan_id: Mapped[int] = mapped_column(
        ForeignKey("loans.id", ondelete="CASCADE"), 
        nullable=False, 
        index=True
    )
    
    generated_letter: Mapped[str] = mapped_column(Text, nullable=False) # Content of draft hardship letter
    model_used: Mapped[str] = mapped_column(String(100), nullable=False, default="Gemini-Pro") # Model descriptor
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now(), 
        nullable=False
    )

    # Relationships
    loan: Mapped["Loan"] = relationship(back_populates="ai_negotiations")

    def __repr__(self) -> str:
        return f"<AINegotiation(id={self.id}, loan_id={self.loan_id}, model_used='{self.model_used}')>"
