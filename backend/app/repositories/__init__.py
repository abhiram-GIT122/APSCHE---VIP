from app.repositories.base import BaseRepository
from app.repositories.user import UserRepository, user_repository
from app.repositories.financial_profile import (
    FinancialProfileRepository,
    financial_profile_repository,
)
from app.repositories.loan import LoanRepository, loan_repository
from app.repositories.settlement_prediction import (
    SettlementPredictionRepository,
    settlement_prediction_repository,
)
from app.repositories.ai_negotiation import (
    AINegotiationRepository,
    ai_negotiation_repository,
)
from app.repositories.ai_history import (
    AIHistoryRepository,
    ai_history_repository,
)

__all__ = [
    "BaseRepository",
    "UserRepository",
    "user_repository",
    "FinancialProfileRepository",
    "financial_profile_repository",
    "LoanRepository",
    "loan_repository",
    "SettlementPredictionRepository",
    "settlement_prediction_repository",
    "AINegotiationRepository",
    "ai_negotiation_repository",
    "AIHistoryRepository",
    "ai_history_repository",
]
