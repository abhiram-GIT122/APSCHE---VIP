from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.financial_profile import FinancialProfile
from app.repositories.base import BaseRepository

class FinancialProfileRepository(BaseRepository[FinancialProfile]):
    """FinancialProfileRepository managing SQL operations for the FinancialProfile model."""
    
    def __init__(self):
        super().__init__(FinancialProfile)

    async def get_by_user_id(self, db: AsyncSession, user_id: int) -> Optional[FinancialProfile]:
        """Fetch the unique financial profile details associated with a specific user ID."""
        query = select(self.model).where(self.model.user_id == user_id)
        result = await db.execute(query)
        return result.scalar_one_or_none()

# Global instance for easy import and reuse
financial_profile_repository = FinancialProfileRepository()
