from datetime import datetime
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict, model_validator, AnyUrl

class SettlementPredictionBase(BaseModel):
    """Shared base properties for Settlement validations."""
    suggested_settlement_percentage: Decimal = Field(..., ge=0, le=100, description="Target settlement percentage (e.g. 45.00 for 45%)")
    risk_score: Decimal = Field(default=Decimal("0.00"), ge=0, le=100, description="Calculated risk score")
    risk_category: str = Field(..., max_length=50, description="Risk category (Low, Medium, High)")
    final_offer_amount: Decimal = Field(..., ge=0, description="Suggested settlement final offer amount")

    # Legacy attributes compatibility property properties
    @property
    def suggested_settlement(self) -> Decimal:
        return self.suggested_settlement_percentage

    @property
    def predicted_amount(self) -> Decimal:
        return self.final_offer_amount

class SettlementPredictionCreate(SettlementPredictionBase):
    """Schema for validating prediction creation inputs."""
    loan_id: int = Field(..., description="ID of the target loan")

class SettlementPredictionUpdate(BaseModel):
    """Schema for validating updates. All fields are optional."""
    suggested_settlement_percentage: Optional[Decimal] = Field(None, ge=0, le=100)
    risk_score: Optional[Decimal] = Field(None, ge=0, le=100)
    risk_category: Optional[str] = Field(None, max_length=50)
    final_offer_amount: Optional[Decimal] = Field(None, ge=0)

class SettlementPredictionResponse(BaseModel):
    """Schema for serializing prediction records in API responses."""
    id: int
    loan_id: int
    suggested_settlement_percentage: Decimal
    risk_score: Decimal
    risk_category: str
    final_offer_amount: Decimal
    created_at: datetime
    explanation: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

    # Convert database ORM attributes to target JSON format keys
    @model_validator(mode="before")
    @classmethod
    def convert_fields(cls, data: any) -> any:
        if isinstance(data, dict):
            return {
                "id": data.get("id") or data.get("settlement_id") or 0,
                "loan_id": data.get("loan_id") or 0,
                "suggested_settlement_percentage": data.get("suggested_settlement_percentage") or data.get("suggested_settlement") or Decimal("0.00"),
                "risk_score": data.get("risk_score") or Decimal("0.00"),
                "risk_category": data.get("risk_category") or "Medium",
                "final_offer_amount": data.get("final_offer_amount") or data.get("predicted_amount") or Decimal("0.00"),
                "created_at": data.get("created_at") or data.get("predicted_date") or datetime.now(),
                "explanation": data.get("explanation")
            }
        # It's an ORM object
        return {
            "id": getattr(data, "id", None) or getattr(data, "settlement_id", 0),
            "loan_id": data.loan_id,
            "suggested_settlement_percentage": getattr(data, "suggested_settlement_percentage", None) or getattr(data, "suggested_settlement", Decimal("0.00")),
            "risk_score": getattr(data, "risk_score", Decimal("0.00")),
            "risk_category": data.risk_category,
            "final_offer_amount": getattr(data, "final_offer_amount", None) or getattr(data, "predicted_amount", Decimal("0.00")),
            "created_at": getattr(data, "created_at", None) or getattr(data, "predicted_date", datetime.now()),
            "explanation": getattr(data, "explanation", None)
        }
