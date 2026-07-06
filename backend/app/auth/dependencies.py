from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.auth.jwt import verify_token
from app.database.session import get_db
from app.repositories.user import user_repository
from app.models.user import User

# Configure clean JWT HTTP Bearer security scheme for Swagger UI
security_scheme = HTTPBearer(auto_error=True)

async def get_current_user(
    db: AsyncSession = Depends(get_db),
    token_credentials: HTTPAuthorizationCredentials = Depends(security_scheme)
) -> User:
    """Dependency verifying access token and returning the current authenticated User.
    
    Raises:
        HTTPException: 401 Unauthorized if token validation fails.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    # Extract token string from Authorization header credentials
    token = token_credentials.credentials if token_credentials else None
    if not token:
        raise credentials_exception
        
    # Defensively strip 'Bearer ' in case user entered 'Bearer <token>' in the Swagger Authorize box
    if token.lower().startswith("bearer "):
        token = token[7:].strip()
    else:
        token = token.strip()
        
    # Decrypt subject (UserID string)
    user_id_str = verify_token(token)
    if user_id_str is None:
        raise credentials_exception
        
    try:
        user_id = int(user_id_str)
    except ValueError:
        raise credentials_exception

    # Query User from Repository
    user = await user_repository.get_by_id(db, user_id)
    if user is None:
        raise credentials_exception
        
    return user
