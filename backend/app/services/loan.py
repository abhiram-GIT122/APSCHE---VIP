import logging
from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.loan import Loan
from app.schemas.loan import LoanCreate, LoanUpdate
from app.repositories.loan import LoanRepository, loan_repository
from app.services.financial_profile_service import FinancialProfileService, financial_profile_service

logger = logging.getLogger("app.services.loan")

class LoanService:
    """Handles CRUD logic for loan records and coordinates dynamic recalculation of financial profiles."""
    
    def __init__(self, repo: LoanRepository = loan_repository, profile_service: FinancialProfileService = financial_profile_service):
        self.repo = repo
        self.profile_service = profile_service

    async def get_loans_by_user(self, db: AsyncSession, user_id: int) -> List[Loan]:
        """Fetch all loans belonging to a specific user."""
        return await self.repo.get_by_user_id(db, user_id)

    async def get_loan_by_id(self, db: AsyncSession, loan_id: int) -> Optional[Loan]:
        """Fetch details of a single loan record."""
        return await self.repo.get_by_id(db, loan_id)

    async def create_loan(self, db: AsyncSession, user_id: int, loan_in: LoanCreate) -> Loan:
        """Saves a new loan record and triggers a recalculation of the user's debt ratios."""
        db_loan = Loan(
            user_id=user_id,
            lender_name=loan_in.lender_name,
            loan_type=loan_in.loan_type,
            principal_amount=loan_in.principal_amount,
            outstanding_amount=loan_in.outstanding_amount,
            interest_rate=loan_in.interest_rate,
            emi_amount=loan_in.emi_amount,
            tenure_months=loan_in.tenure_months,
            overdue_months=loan_in.overdue_months,
            status=loan_in.status
        )
        created_loan = await self.repo.create(db, db_loan)
        logger.info(f"Loan ID {created_loan.id} created for user ID: {user_id}")
        
        # Trigger recalculation of ratios safely (non-blocking)
        try:
            await self.profile_service.recalculate_profile(db, user_id)
        except Exception as e:
            logger.error(f"Soft error: Financial profile recalculation failed during loan creation for user {user_id}: {e}", exc_info=True)
        return created_loan

    async def update_loan(self, db: AsyncSession, loan_id: int, loan_update: LoanUpdate) -> Optional[Loan]:
        """Updates parameters of a loan record and recalculates user ratios."""
        db_loan = await self.repo.get_by_id(db, loan_id)
        if not db_loan:
            return None

        update_dict = loan_update.model_dump(exclude_unset=True)
        # Handle legacy emi to emi_amount conversion if passed in update dict
        if "emi" in update_dict and "emi_amount" not in update_dict:
            update_dict["emi_amount"] = update_dict.pop("emi")
            
        updated_loan = await self.repo.update(db, db_loan, update_dict)
        logger.info(f"Loan ID {loan_id} updated for user ID: {updated_loan.user_id}")
        
        # Trigger recalculation of ratios safely (non-blocking)
        try:
            await self.profile_service.recalculate_profile(db, updated_loan.user_id)
        except Exception as e:
            logger.error(f"Soft error: Financial profile recalculation failed during loan update for user {updated_loan.user_id}: {e}", exc_info=True)
        return updated_loan

    async def delete_loan(self, db: AsyncSession, loan_id: int) -> bool:
        """Removes a loan record and triggers recalculation of ratios."""
        db_loan = await self.repo.get_by_id(db, loan_id)
        if not db_loan:
            return False

        user_id = db_loan.user_id
        await self.repo.delete(db, db_loan)
        logger.info(f"Loan ID {loan_id} deleted for user ID: {user_id}")
        
        # Trigger recalculation of ratios safely (non-blocking)
        try:
            await self.profile_service.recalculate_profile(db, user_id)
        except Exception as e:
            logger.error(f"Soft error: Financial profile recalculation failed during loan deletion for user {user_id}: {e}", exc_info=True)
        return True

    async def get_user_loan_summary(self, db: AsyncSession, user_id: int) -> Dict[str, Any]:
        """Aggregates and processes all user loan data to produce a summary of active debt."""
        from decimal import Decimal
        loans = await self.get_loans_by_user(db, user_id)
        
        status_breakdown = {"active": 0, "closed": 0, "defaulted": 0}
        total_loan_amount = Decimal("0.00")
        total_monthly_emi = Decimal("0.00")
        active_loans = 0

        for loan in loans:
            # Respect stored status defaults, closed, or defaults past-due months
            status = loan.status or "active"
            if loan.outstanding_amount <= 0:
                status = "closed"
            elif loan.overdue_months >= 3:
                status = "defaulted"
                
            status_breakdown[status] += 1
            
            if status == "active":
                total_loan_amount += loan.outstanding_amount
                total_monthly_emi += loan.emi_amount
                active_loans += 1

        return {
            "total_loan_amount": float(total_loan_amount),
            "total_monthly_emi": float(total_monthly_emi),
            "active_loans": active_loans,
            "status_breakdown": status_breakdown
        }

# Global singleton instance
loan_service = LoanService()
