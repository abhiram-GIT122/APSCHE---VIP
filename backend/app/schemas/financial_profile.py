from datetime import datetime
from decimal import Decimal
from typing import Optional, Any
from pydantic import BaseModel, Field, ConfigDict, model_validator

class FinancialProfileBase(BaseModel):
    """Shared base properties for FinancialProfile validations."""
    emi_ratio: Decimal = Field(default=Decimal("0.00"), ge=0, le=100, description="EMI to Income ratio percentage")
    dti_ratio: Decimal = Field(default=Decimal("0.00"), ge=0, le=100, description="Debt to Income ratio percentage")
    monthly_surplus: Decimal = Field(default=Decimal("0.00"), description="Monthly cash surplus in USD")
    stress_level: str = Field(default="Low", max_length=50, description="Financial stress flag (Low, Moderate, Severe, Critical)")

class FinancialProfileCreate(FinancialProfileBase):
    """Schema for validating profile creation inputs."""
    user_id: int = Field(..., description="ID of the associated user")

class FinancialProfileUpdate(BaseModel):
    """Schema for validating profile updates. All fields are optional."""
    emi_ratio: Optional[Decimal] = Field(None, ge=0, le=100)
    dti_ratio: Optional[Decimal] = Field(None, ge=0, le=100)
    monthly_surplus: Optional[Decimal] = None
    stress_level: Optional[str] = Field(None, max_length=50)

class FinancialProfileResponse(BaseModel):
    """Schema for serializing financial profiles in API responses."""
    profile_id: int
    user_id: int
    emi_ratio: float
    dti_ratio: float
    monthly_surplus: float
    stress_level: str
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

    @model_validator(mode="before")
    @classmethod
    def convert_fields(cls, data: Any) -> Any:
        if isinstance(data, dict):
            return {
                **data,
                "emi_ratio": float(data.get("emi_ratio") or 0.0) / 100.0,
                "dti_ratio": float(data.get("dti_ratio") or 0.0) / 100.0,
                "monthly_surplus": float(data.get("monthly_surplus") or 0.0),
                "stress_level": str(data.get("stress_level") or "LOW").upper()
            }
        return {
            "profile_id": data.profile_id,
            "user_id": data.user_id,
            "emi_ratio": float(data.emi_ratio) / 100.0 if data.emi_ratio else 0.0,
            "dti_ratio": float(data.dti_ratio) / 100.0 if data.dti_ratio else 0.0,
            "monthly_surplus": float(data.monthly_surplus) if data.monthly_surplus else 0.0,
            "stress_level": (data.stress_level or "LOW").upper(),
            "updated_at": data.updated_at
        }
