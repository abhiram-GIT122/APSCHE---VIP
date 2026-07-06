from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.settlement import Settlement
from app.repositories.base import BaseRepository

class SettlementPredictionRepository(BaseRepository[Settlement]):
    """SettlementPredictionRepository managing SQL operations for Settlement records."""
    
    def __init__(self):
        super().__init__(Settlement)

    async def get_by_loan_id(self, db: AsyncSession, loan_id: int) -> List[Settlement]:
        """Fetch all settlement terms predictions registered for a specific loan ID."""
        query = select(self.model).where(self.model.loan_id == loan_id)
        result = await db.execute(query)
        return list(result.scalars().all())

# Global instance for easy import and reuse
settlement_prediction_repository = SettlementPredictionRepository()
