from passlib.context import CryptContext

# Set up password hashing context using bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against the stored bcrypt hash.
    
    Args:
        plain_password: Cleartext password.
        hashed_password: Stored bcrypt hash.
        
    Returns:
        bool: True if password matches, False otherwise.
    """
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Generates a secure bcrypt hash for a password.
    
    Args:
        password: Cleartext password.
        
    Returns:
        str: Bcrypt hash.
    """
    return pwd_context.hash(password)
