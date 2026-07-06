# Centralized API dependencies file
from app.database.session import get_db
from app.auth.dependencies import get_current_user

__all__ = ["get_db", "get_current_user"]
