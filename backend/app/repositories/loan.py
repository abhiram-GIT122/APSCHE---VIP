from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.loan import Loan
from app.repositories.base import BaseRepository

class LoanRepository(BaseRepository[Loan]):
    """LoanRepository managing SQL operations for Loan records."""
    
    def __init__(self):
        super().__init__(Loan)

    async def get_by_user_id(self, db: AsyncSession, user_id: int) -> List[Loan]:
        """Fetch all outstanding loan liabilities associated with a specific user ID."""
        query = select(self.model).where(self.model.user_id == user_id)
        result = await db.execute(query)
        return list(result.scalars().all())

# Global instance for easy import and reuse
loan_repository = LoanRepository()
