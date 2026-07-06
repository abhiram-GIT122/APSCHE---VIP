from datetime import datetime
from typing import Optional
from decimal import Decimal
from pydantic import BaseModel, Field, ConfigDict, model_validator

class AINegotiationBase(BaseModel):
    """Shared base properties for AINegotiation validations."""
    model_used: str = Field(default="Gemini-Pro", min_length=1, max_length=100, description="Model or strategy descriptor")
    generated_letter: str = Field(..., description="Legal proposal content draft letter")

    # Legacy attributes compatibility property properties
    @property
    def negotiation_strategy(self) -> str:
        return self.model_used

    @property
    def negotiation_letter(self) -> str:
        return self.generated_letter

class AINegotiationCreate(BaseModel):
    """Schema for validating negotiation generation requests."""
    loan_id: int = Field(..., description="ID of the target loan liability")
    negotiation_strategy: str = Field(default="Hardship", min_length=1, max_length=100, description="Strategy code (e.g., Hardship, Settlement Proposal)")

class AINegotiationUpdate(BaseModel):
    """Schema for updating negotiation details."""
    model_used: Optional[str] = Field(None, min_length=1, max_length=100)
    generated_letter: Optional[str] = None

class AINegotiationResponse(BaseModel):
    """Schema for serializing negotiation letters in API responses."""
    id: int
    loan_id: int
    generated_letter: str
    model_used: str
    created_at: datetime
    recommended_offer: Optional[Decimal] = None
    explanation: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

    # Convert database ORM attributes to target JSON format keys
    @model_validator(mode="before")
    @classmethod
    def convert_fields(cls, data: any) -> any:
        if isinstance(data, dict):
            return {
                "id": data.get("id") or data.get("ai_id") or 0,
                "loan_id": data.get("loan_id") or 0,
                "generated_letter": data.get("generated_letter") or data.get("negotiation_letter") or "",
                "model_used": data.get("model_used") or data.get("negotiation_strategy") or "Gemini-Pro",
                "created_at": data.get("created_at") or data.get("generated_date") or datetime.now(),
                "recommended_offer": data.get("recommended_offer"),
                "explanation": data.get("explanation")
            }
        # It's an ORM object
        return {
            "id": getattr(data, "id", None) or getattr(data, "ai_id", 0),
            "loan_id": data.loan_id,
            "generated_letter": getattr(data, "generated_letter", None) or getattr(data, "negotiation_letter", ""),
            "model_used": getattr(data, "model_used", None) or getattr(data, "negotiation_strategy", "Gemini-Pro"),
            "created_at": getattr(data, "created_at", None) or getattr(data, "generated_date", datetime.now()),
            "recommended_offer": getattr(data, "recommended_offer", None),
            "explanation": getattr(data, "explanation", None)
        }
