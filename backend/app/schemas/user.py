from datetime import datetime
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, ConfigDict

class UserBase(BaseModel):
    """Shared base properties for User validations."""
    name: str = Field(..., min_length=1, max_length=100, description="Full name of the user")
    email: EmailStr = Field(..., description="Unique email address")
    monthly_income: Decimal = Field(default=Decimal("0.00"), ge=0, description="Monthly income in USD")
    monthly_expenses: Decimal = Field(default=Decimal("0.00"), ge=0, description="Monthly fixed expenses in USD")

class UserCreate(UserBase):
    """Schema for validating user registration inputs."""
    password: str = Field(..., min_length=8, max_length=100, description="User password (min 8 chars)")

class UserUpdate(BaseModel):
    """Schema for validating user profile update inputs. All fields are optional."""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    email: Optional[EmailStr] = None
    monthly_income: Optional[Decimal] = Field(None, ge=0)
    monthly_expenses: Optional[Decimal] = Field(None, ge=0)
    password: Optional[str] = Field(None, min_length=8, max_length=100)

class UserResponse(UserBase):
    """Schema for serializing user records in API responses."""
    id: int
    created_at: datetime
    updated_at: datetime

    # Enable ORM attribute loading
    model_config = ConfigDict(from_attributes=True)
