import logging
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.schemas.user import UserCreate
from app.repositories.user import UserRepository, user_repository
from app.services.user import UserService, user_service
from app.core.security import verify_password
from app.auth.jwt import create_access_token

logger = logging.getLogger("app.auth.service")

class AuthService:
    """Manages business operations orchestrating user login verification and account creation."""
    
    def __init__(self, user_repo: UserRepository = user_repository, usr_service: UserService = user_service):
        self.user_repo = user_repo
        self.usr_service = usr_service

    async def register(self, db: AsyncSession, user_in: UserCreate) -> User:
        """Saves a new user profile using the default user service."""
        logger.info(f"Delegating user registration for: {user_in.email}")
        return await self.usr_service.register_user(db, user_in)

    async def authenticate_and_create_token(self, db: AsyncSession, email: str, password: str) -> Optional[str]:
        """Validates credentials. Generates a signed JWT access token on success.
        
        Returns:
            str: Signed JWT access token, or None if authentication fails.
        """
        # Fetch user
        user = await self.user_repo.get_by_email(db, email)
        if not user:
            logger.warning(f"Failed login attempt: Email '{email}' not registered.")
            return None

        # Verify password
        print("=" * 50)
        print("EMAIL:", email)
        print("PASSWORD TYPE:", type(password))
        print("PASSWORD:", repr(password))
        print("PASSWORD LENGTH:", len(password))
        print("HASH:", repr(user.hashed_password))
        print("HASH LENGTH:", len(user.hashed_password))
        print("=" * 50)              
        if not verify_password(password, user.hashed_password):
            logger.warning(f"Failed login attempt: Incorrect password for '{email}'.")
            return None

        # Create JWT access token. Subject is User ID
        token = create_access_token(user.id)
        logger.info(f"User ID {user.id} authenticated successfully. Access token generated.")
        return token

# Global singleton instance
auth_service = AuthService()
