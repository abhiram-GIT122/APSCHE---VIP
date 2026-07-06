from pydantic import BaseModel, Field, EmailStr
from typing import Optional

class Token(BaseModel):
    """Payload schema returned on successful login."""
    access_token: str = Field(..., description="JWT Bearer access token string")
    token_type: str = Field(default="bearer", description="Token authentication scheme")

class TokenPayload(BaseModel):
    """Parsed internal data structure of the JWT payload."""
    sub: Optional[str] = Field(None, description="Subject identifier (User ID)")
    exp: Optional[int] = Field(None, description="Expiration timestamp (unix time)")

class LoginRequest(BaseModel):
    """Payload schema for user authentication requests."""
    email: EmailStr = Field(..., description="User's unique email address")
    password: str = Field(..., description="User's account password")
