from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.ai_history import AIHistory
from app.repositories.base import BaseRepository

class AIHistoryRepository(BaseRepository[AIHistory]):
    """AIHistoryRepository managing SQL operations for logging AI audit items."""
    
    def __init__(self):
        super().__init__(AIHistory)

    async def get_by_user_id(self, db: AsyncSession, user_id: int, skip: int = 0, limit: int = 100) -> List[AIHistory]:
        """Fetch audit log history entries linked to a user, sorted by descending timestamps."""
        query = (
            select(self.model)
            .where(self.model.user_id == user_id)
            .order_by(self.model.timestamp.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await db.execute(query)
        return list(result.scalars().all())

    async def delete_all_by_user_id(self, db: AsyncSession, user_id: int) -> bool:
        """Delete all history entries belonging to a user."""
        from sqlalchemy import delete
        query = delete(self.model).where(self.model.user_id == user_id)
        await db.execute(query)
        await db.commit()
        return True

# Global instance for easy import and reuse
ai_history_repository = AIHistoryRepository()
