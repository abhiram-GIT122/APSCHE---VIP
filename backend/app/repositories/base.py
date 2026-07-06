from typing import TypeVar, Generic, Type, Optional, List, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.base import Base

ModelType = TypeVar("ModelType", bound=Base)

class BaseRepository(Generic[ModelType]):
    """Generic repository implementing standard asynchronous CRUD operations for database access."""
    
    def __init__(self, model: Type[ModelType]):
        """Initializes the repository with the target SQLAlchemy model type."""
        self.model = model

    async def get_by_id(self, db: AsyncSession, id: Any) -> Optional[ModelType]:
        """Fetch a single record by its primary key.
        
        Uses db.get which automatically resolves the primary key column name.
        """
        return await db.get(self.model, id)

    async def get_all(self, db: AsyncSession, skip: int = 0, limit: int = 100) -> List[ModelType]:
        """Fetch all records with optional pagination limits."""
        query = select(self.model).offset(skip).limit(limit)
        result = await db.execute(query)
        return list(result.scalars().all())

    async def create(self, db: AsyncSession, db_obj: ModelType) -> ModelType:
        """Create a new database record and commits it."""
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def update(self, db: AsyncSession, db_obj: ModelType, update_data: dict) -> ModelType:
        """Update fields of an existing model instance and commits the changes."""
        for field, value in update_data.items():
            if hasattr(db_obj, field):
                setattr(db_obj, field, value)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def delete(self, db: AsyncSession, db_obj: ModelType) -> bool:
        """Delete an existing model instance from the database."""
        await db.delete(db_obj)
        await db.commit()
        return True
