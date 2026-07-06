import logging
from decimal import Decimal
from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.models.loan import Loan
from app.models.financial_profile import FinancialProfile
from app.repositories.financial_profile import FinancialProfileRepository, financial_profile_repository
from app.repositories.user import UserRepository, user_repository
from app.repositories.loan import LoanRepository, loan_repository

logger = logging.getLogger("app.services.financial_profile_service")

def calculate_financial_health(user: User, loans: List[Loan]) -> Dict[str, Any]:
    """Calculates user's monthly surplus, active debt ratios, and stress category.
    
    Ratios are represented as decimal values (e.g. 0.35 for 35%).
    Only ACTIVE loans are used for financial calculations unless explicitly required.
    Risk scoring depends on the number of active loans.
    """
    # Force safety on user budget numbers
    income_val = getattr(user, "monthly_income", Decimal("0.00"))
    if income_val is None:
        income_val = Decimal("0.00")
    monthly_income = Decimal(str(income_val))
    if monthly_income < Decimal("0.00"):
        monthly_income = Decimal("0.00")

    expenses_val = getattr(user, "monthly_expenses", Decimal("0.00"))
    if expenses_val is None:
        expenses_val = Decimal("0.00")
    monthly_expenses = Decimal(str(expenses_val))
    if monthly_expenses < Decimal("0.00"):
        monthly_expenses = Decimal("0.00")

    # 1. Calculate monthly_surplus = user.monthly_income - user.monthly_expenses
    monthly_surplus = monthly_income - monthly_expenses

    # 2. Extract active loans and calculate total monthly EMI
    status_breakdown = {"active": 0, "closed": 0, "defaulted": 0}
    total_monthly_debt_payments = Decimal("0.00")
    active_loans = 0

    for loan in loans:
        # Protect against None or missing loan values
        out_val = getattr(loan, "outstanding_amount", Decimal("0.00"))
        if out_val is None:
            out_val = Decimal("0.00")
        outstanding_amount = Decimal(str(out_val))

        emi_val = getattr(loan, "emi_amount", Decimal("0.00"))
        if emi_val is None:
            emi_val = Decimal("0.00")
        emi_amount = Decimal(str(emi_val))

        overdue_months = getattr(loan, "overdue_months", 0)
        if overdue_months is None:
            overdue_months = 0
        try:
            overdue_months = int(overdue_months)
        except ValueError:
            overdue_months = 0

        status = getattr(loan, "status", "active")
        if not status:
            status = "active"
        status = status.lower()

        if outstanding_amount <= Decimal("0.00"):
            status = "closed"
        elif overdue_months >= 3:
            status = "defaulted"
            
        status_breakdown[status] += 1
        
        if status == "active":
            total_monthly_debt_payments += emi_amount
            active_loans += 1

    # 3. Compute dti_ratio & emi_ratio = total_debt_payments (active only) / monthly_income
    if monthly_income > Decimal("0.00"):
        dti_ratio = total_monthly_debt_payments / monthly_income
        emi_ratio = total_monthly_debt_payments / monthly_income
    else:
        dti_ratio = Decimal("1.00") if total_monthly_debt_payments > Decimal("0.00") else Decimal("0.00")
        emi_ratio = Decimal("1.00") if total_monthly_debt_payments > Decimal("0.00") else Decimal("0.00")

    # 4. Determine stress_level from DTI ratio
    if dti_ratio < Decimal("0.30"):
        stress_level = "LOW"
    elif dti_ratio <= Decimal("0.50"):
        stress_level = "MEDIUM"
    else:
        stress_level = "HIGH"

    # 5. Risk scoring upgrade depending on the count of active loans
    if active_loans >= 5:
        stress_level = "HIGH"
    elif active_loans >= 3 and stress_level == "LOW":
        stress_level = "MEDIUM"

    return {
        "emi_ratio": float(emi_ratio),
        "dti_ratio": float(dti_ratio),
        "monthly_surplus": float(monthly_surplus),
        "stress_level": stress_level
    }

class FinancialProfileService:
    """Manages business calculations representing user financial stress indices and debt obligations ratios."""
    
    def __init__(
        self, 
        repo: FinancialProfileRepository = financial_profile_repository,
        user_repo: UserRepository = user_repository,
        loan_repo: LoanRepository = loan_repository
    ):
        self.repo = repo
        self.user_repo = user_repo
        self.loan_repo = loan_repo

    async def get_profile_by_user_id(self, db: AsyncSession, user_id: int) -> Optional[FinancialProfile]:
        """Fetch the financial profile associated with a specific user ID."""
        return await self.repo.get_by_user_id(db, user_id)

    async def recalculate_profile(self, db: AsyncSession, user_id: int) -> Optional[FinancialProfile]:
        """Performs analytical calculation updates mapping user income against total debt liabilities."""
        # Fetch target user
        user = await self.user_repo.get_by_id(db, user_id)
        if not user:
            logger.warning(f"Failed to recalculate profile: User ID {user_id} not found.")
            return None

        # Fetch active profile
        profile = await self.repo.get_by_user_id(db, user_id)
        if not profile:
            # Create a profile if it does not exist
            profile = FinancialProfile(user_id=user_id)
            await self.repo.create(db, profile)

        # Fetch all loans for this user
        loans = await self.loan_repo.get_by_user_id(db, user_id)

        # Calculate using modular health engine helper
        health = calculate_financial_health(user, loans)

        # Apply parameters to profile object (converting back to percentages for DB compatibility where needed)
        update_data = {
            "emi_ratio": Decimal(str(health["emi_ratio"])) * Decimal("100.00"),
            "dti_ratio": Decimal(str(health["dti_ratio"])) * Decimal("100.00"),
            "monthly_surplus": Decimal(str(health["monthly_surplus"])),
            "stress_level": health["stress_level"].title() # Convert "LOW", "MEDIUM", "HIGH" to "Low", "Medium", "High"
        }
        
        updated_profile = await self.repo.update(db, profile, update_data)
        logger.info(f"Financial profile recalculated for user ID {user_id}: DTI={health['dti_ratio']*100:.2f}%, Stress={health['stress_level']}")
        
        # Integrate with financial profile system so it can optionally be called after calculation
        try:
            from app.services.settlement_service import calculate_settlement_offer
            from app.services.loan import loan_service
            loan_summary = await loan_service.get_user_loan_summary(db, user_id)
            settlement_offer = calculate_settlement_offer(updated_profile, loan_summary)
            logger.info(f"Settlement offer recommendation calculated: risk={settlement_offer['risk_level']}, amount=${settlement_offer['settlement_amount']:.2f}")
        except Exception as exc:
            logger.warning(f"Failed to calculate settlement offer during profile recalculation: {str(exc)}")
            
        return updated_profile

# Global singleton instance
financial_profile_service = FinancialProfileService()
