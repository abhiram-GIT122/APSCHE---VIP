from app.models.user import User
from app.models.loan import Loan
from app.models.financial_profile import FinancialProfile
from app.models.negotiation import NegotiationHistory
from app.models.settlement import SettlementRecommendation

# Aliases to avoid naming conflicts with routers
negotiation_model = NegotiationHistory  # noqa: F401
settlement_model = SettlementRecommendation  # noqa: F401

__all__ = [
    "User",
    "Loan",
    "FinancialProfile",
    "NegotiationHistory",
    "SettlementRecommendation",
]
