import logging
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.models.financial_profile import FinancialProfile
from app.schemas.user import UserCreate, UserUpdate
from app.repositories.user import UserRepository, user_repository
from app.repositories.financial_profile import FinancialProfileRepository, financial_profile_repository
from app.core.security import get_password_hash, verify_password

logger = logging.getLogger("app.services.user")

class UserService:
    """Handles business logic operations for User records and profile registration."""
    
    def __init__(self, repo: UserRepository = user_repository, profile_repo: FinancialProfileRepository = financial_profile_repository):
        self.repo = repo
        self.profile_repo = profile_repo

    async def register_user(self, db: AsyncSession, user_in: UserCreate) -> User:
        """Registers a new user account, hashes their password, and creates an empty financial profile."""
        existing_user = await self.repo.get_by_email(db, user_in.email)
        if existing_user:
            raise ValueError(f"A user with email '{user_in.email}' is already registered.")

        # Hash credentials
        hashed_password = get_password_hash(user_in.password)
        db_user = User(
            name=user_in.name,
            email=user_in.email,
            hashed_password=hashed_password,
            monthly_income=user_in.monthly_income,
            monthly_expenses=user_in.monthly_expenses
        )
        
        # Save user record
        created_user = await self.repo.create(db, db_user)
        logger.info(f"User registered with ID: {created_user.id}")

        # Create initial financial profile matching the user
        initial_profile = FinancialProfile(
            user_id=created_user.id,
            emi_ratio=0.00,
            dti_ratio=0.00,
            monthly_surplus=created_user.monthly_income - created_user.monthly_expenses,
            stress_level="Low"
        )
        await self.profile_repo.create(db, initial_profile)
        logger.info(f"Initial financial profile created for user ID: {created_user.id}")

        return created_user

    async def authenticate(self, db: AsyncSession, email: str, password: str) -> Optional[User]:
        """Validates credentials against stored passwords."""
        user = await self.repo.get_by_email(db, email)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user

    async def get_user_by_id(self, db: AsyncSession, user_id: int) -> Optional[User]:
        """Fetch user by ID."""
        return await self.repo.get_by_id(db, user_id)

    async def update_user(self, db: AsyncSession, user_id: int, user_update: UserUpdate) -> Optional[User]:
        """Updates user profile data. Triggers financial profile calculations if income/expenses change."""
        db_user = await self.repo.get_by_id(db, user_id)
        if not db_user:
            return None

        update_dict = user_update.model_dump(exclude_unset=True)
        
        # Handle password update
        if "password" in update_dict and update_dict["password"]:
            update_dict["hashed_password"] = get_password_hash(update_dict.pop("password"))
        elif "password" in update_dict:
            update_dict.pop("password")

        # Perform update
        updated_user = await self.repo.update(db, db_user, update_dict)
        logger.info(f"User profile updated for user ID: {user_id}")

        # If budgets are altered, trigger dynamic calculations (implemented in FinancialProfileService)
        return updated_user

# Global singleton instance
user_service = UserService()
