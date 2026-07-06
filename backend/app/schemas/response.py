from typing import Generic, TypeVar, Optional
from pydantic import BaseModel

T = TypeVar("T")

class StandardResponse(BaseModel, Generic[T]):
    """Standardized envelope schema for all HTTP JSON responses."""
    success: bool
    data: Optional[T] = None
    message: str = ""
