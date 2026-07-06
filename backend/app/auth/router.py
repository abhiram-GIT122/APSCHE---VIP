from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Any

from app.api.dependencies import get_db
from app.auth.service import auth_service
from app.auth.schemas import Token, LoginRequest
from app.schemas.user import UserCreate, UserResponse
from app.schemas.response import StandardResponse

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=StandardResponse[UserResponse], status_code=status.HTTP_201_CREATED)
async def register(
    user_in: UserCreate,
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Registers a new user account and creates their initial financial profile."""
    try:
        new_user = await auth_service.register(db, user_in)
        return {
            "success": True,
            "data": new_user,
            "message": "User registered successfully"
        }
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc)
        )

@router.post("/login", response_model=StandardResponse[Token])
async def login(
    request_in: LoginRequest,
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Authenticates email and password, returning a JWT access token."""
    token = await auth_service.authenticate_and_create_token(
        db, 
        email=request_in.email, 
        password=request_in.password
    )
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return {
        "success": True,
        "data": {"access_token": token, "token_type": "bearer"},
        "message": "Login successful"
    }
