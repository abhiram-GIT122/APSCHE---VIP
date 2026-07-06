from datetime import datetime, timedelta, timezone
from typing import Any, Union, Optional
from jose import jwt, JWTError
from app.config.config import settings

# Enforcing standard cryptographic encryption algorithm
ALGORITHM = "HS256"

def create_access_token(subject: Union[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Encodes a JWT payload with expiration boundaries.
    
    Args:
        subject: The payload identity subject (e.g. user_id).
        expires_delta: Optional token lifetime override.
        
    Returns:
        str: Encrypted token string.
    """
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode = {
        "exp": int(expire.timestamp()),
        "sub": str(subject)
    }
    
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str) -> Optional[str]:
    """Decrypts a token payload and retrieves the subject identifier.
    
    Returns:
        str: Subject string if verified, otherwise None.
    """
    try:
        # Decode token with 60 seconds clock skew leeway
        payload = jwt.decode(
            token, 
            settings.SECRET_KEY, 
            algorithms=[ALGORITHM],
            options={"leeway": 60}
        )
        token_sub = payload.get("sub")
        return token_sub
    except JWTError:
        return None
