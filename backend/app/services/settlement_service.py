import logging
from decimal import Decimal
from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.models.loan import Loan
from app.models.settlement import Settlement
from app.models.financial_profile import FinancialProfile
from app.models.ai_history import AIHistory
from app.repositories.settlement_prediction import SettlementPredictionRepository, settlement_prediction_repository
from app.repositories.loan import LoanRepository, loan_repository
from app.repositories.financial_profile import FinancialProfileRepository, financial_profile_repository
from app.repositories.ai_history import AIHistoryRepository, ai_history_repository
from app.services.financial_profile_service import calculate_financial_health
from app.ai.client import GeminiClient, gemini_client

logger = logging.getLogger("app.services.settlement_service")

def predict_settlement_offer(user: User, loan: Loan) -> Dict[str, Any]:
    """Calculates suggested settlement payout percentages and amounts based on DTI risk bounds.
    
    Logic:
    - Base settlement = 50% of loan amount
    - Adjust based on DTI:
      - HIGH risk (DTI > 0.5) -> 30-50%
      - MEDIUM risk (0.3 <= DTI <= 0.5) -> 50-70%
      - LOW risk (DTI < 0.3) -> 70-85%
    """
    # 1. Base settlement = 50% of loan amount
    base_percentage = Decimal("50.00")
    
    # Compute DTI dynamically from monthly income and loan EMI
    income = user.monthly_income
    emi = loan.emi_amount
    if income > 0:
        dti = emi / income
    else:
        dti = Decimal("1.0")

    # 2. Adjust based on DTI bounds
    if dti > Decimal("0.5"):
        # HIGH risk -> 30-50%
        # Propose lower settlement percentage since user stress is high (midpoint 40%)
        recommended_settlement_percentage = Decimal("40.00")
        reasoning = (
            f"High DTI ratio ({dti*100:.2f}%) indicates severe financial stress. "
            f"Proposing a low settlement percentage of 40% to ease debtor burden and match cash constraints."
        )
    elif dti >= Decimal("0.3"):
        # MEDIUM risk -> 50-70%
        # Midpoint 60%
        recommended_settlement_percentage = Decimal("60.00")
        reasoning = (
            f"Medium DTI ratio ({dti*100:.2f}%) indicates moderate financial stress. "
            f"Proposing a mid-range settlement offer of 60%."
        )
    else:
        # LOW risk -> 70-85%
        # Midpoint 75% or 80% (let's use 75% or 80%, let's use 80% to be standard)
        recommended_settlement_percentage = Decimal("80.00")
        reasoning = (
            f"Low DTI ratio ({dti*100:.2f}%) indicates manageable debt. "
            f"Lender holds strong leverage; proposing an 80% settlement offer."
        )

    # 3. Calculate recommended amount
    recommended_amount = loan.outstanding_amount * (recommended_settlement_percentage / Decimal("100.00"))

    return {
        "recommended_settlement_percentage": float(recommended_settlement_percentage),
        "recommended_amount": float(recommended_amount),
        "reasoning": reasoning
    }

def calculate_settlement_offer(user_profile: FinancialProfile, loan_summary: Dict[str, Any]) -> Dict[str, Any]:
    """Calculates settlement offers based on user financial health and loan totals.
    
    RULES:
    - HIGH risk (DTI > 0.5):
      settlement range = 30% - 50% of total loan (Propose midpoint 40.0)
    - MEDIUM risk (0.3 - 0.5):
      settlement range = 50% - 70% (Propose midpoint 60.0)
    - LOW risk (< 0.3):
      settlement range = 70% - 85% (Propose midpoint 80.0)
    """
    # Import locally to avoid potential circular dependencies
    from app.models.financial_profile import FinancialProfile
    
    # 1. Extract and normalize DTI ratio
    dti = user_profile.dti_ratio
    if dti > Decimal("1.0"):
        dti = dti / Decimal("100.0")
        
    # Determine risk category
    if dti > Decimal("0.5"):
        risk_level = "HIGH"
        settlement_percentage = 40.0
        range_str = "30% - 50%"
    elif dti >= Decimal("0.3"):
        risk_level = "MEDIUM"
        settlement_percentage = 60.0
        range_str = "50% - 70%"
    else:
        risk_level = "LOW"
        settlement_percentage = 80.0
        range_str = "70% - 85%"

    # 2. Get total loan amount from loan summary
    total_loan_amount = loan_summary.get("total_loan_amount", 0.0)
    settlement_amount = float(total_loan_amount) * (settlement_percentage / 100.0)

    # 3. Build explanation reasoning
    reasoning = (
        f"Based on a DTI ratio of {dti*100:.2f}% indicating a {risk_level} risk profile, "
        f"a settlement within the {range_str} range is recommended. "
        f"The proposed target is set at {settlement_percentage}% of the total active loan balance (${total_loan_amount:.2f}), "
        f"which equates to ${settlement_amount:.2f}."
    )

    return {
        "risk_level": risk_level,
        "settlement_percentage": settlement_percentage,
        "settlement_amount": settlement_amount,
        "reasoning": reasoning
    }

class SettlementPredictionService:
    """Orchestrates AI analysis queries to predict loan payout options using client risk vectors."""
    
    def __init__(
        self,
        repo: SettlementPredictionRepository = settlement_prediction_repository,
        loan_repo: LoanRepository = loan_repository,
        profile_repo: FinancialProfileRepository = financial_profile_repository,
        history_repo: AIHistoryRepository = ai_history_repository,
        ai_client: GeminiClient = gemini_client
    ):
        self.repo = repo
        self.loan_repo = loan_repo
        self.profile_repo = profile_repo
        self.history_repo = history_repo
        self.ai_client = ai_client

    async def get_predictions_by_loan(self, db: AsyncSession, loan_id: int) -> List[Settlement]:
        """Fetch settlement predictions linked to a specific loan."""
        return await self.repo.get_by_loan_id(db, loan_id)

    async def get_predictions_by_user(self, db: AsyncSession, user_id: int) -> List[Settlement]:
        """Fetch all settlement predictions for a user's loans."""
        user_loans = await self.loan_repo.get_by_user_id(db, user_id)
        loan_ids = [loan.id for loan in user_loans]
        
        predictions = []
        for lid in loan_ids:
            preds = await self.repo.get_by_loan_id(db, lid)
            predictions.extend(preds)
        return predictions

    async def predict_settlement(self, db: AsyncSession, loan_id: int) -> Optional[Tuple[Settlement, str]]:
        """Orchestrates prediction logic by calling Gemini, or running predict_settlement_offer as fallback."""
        loan = await self.loan_repo.get_by_id(db, loan_id)
        if not loan:
            logger.warning(f"Predict failed: Loan ID {loan_id} not found")
            return None
            
        from app.repositories.user import user_repository
        user = await user_repository.get_by_id(db, loan.user_id)
        if not user:
            logger.warning(f"Predict failed: User not found for Loan ID {loan_id}")
            return None

        profile = await self.profile_repo.get_by_user_id(db, loan.user_id)
        if not profile:
            logger.warning(f"Predict failed: Profile not found for User ID {loan.user_id}")
            return None

        # Try Google Gemini AI first
        target_percentage = Decimal("50.00")
        risk = "Medium"
        explanation = ""
        ai_success = False
        prompt = "Local rule-based fallback triggered because Gemini client is disabled or offline."

        if self.ai_client.api_key:
            try:
                prompt = (
                    f"Analyze settlement probability for the following debtor situation:\n"
                    f"- Lender: {loan.lender_name}\n"
                    f"- Loan Type: {loan.loan_type}\n"
                    f"- Outstanding Balance: ${loan.outstanding_amount:.2f}\n"
                    f"- Current Interest Rate: {loan.interest_rate:.2f}%\n"
                    f"- Monthly EMI obligation: ${loan.emi_amount:.2f}\n"
                    f"- Accounts Overdue Period: {loan.overdue_months} months\n"
                    f"Debtor financial profile metrics:\n"
                    f"- Debt-to-Income (DTI) Ratio: {profile.dti_ratio:.2f}%\n"
                    f"- EMI-to-Income Ratio: {profile.emi_ratio:.2f}%\n"
                    f"- Monthly Cash Surplus: ${profile.monthly_surplus:.2f}\n"
                    f"- Stress Index Flag: {profile.stress_level}\n\n"
                    f"Please output a structured JSON recommendation with 'suggested_settlement_percentage' (0.0 to 100.0), "
                    f"'risk_category' ('Low', 'Medium', 'High'), and a detailed 'rationale' text."
                )
                ai_response = await self.ai_client.generate_settlement_prediction(prompt)
                
                target_percentage = Decimal(str(ai_response.get("suggested_settlement_percentage", "50.0")))
                risk = ai_response.get("risk_category", "Medium")
                explanation = ai_response.get("rationale", "AI generated target settlement based on outstanding balance and stress ratios.")
                ai_success = True
                logger.info(f"Gemini API returned settlement prediction for loan ID {loan_id}.")
            except Exception as exc:
                logger.warning(f"Gemini API query failed: {str(exc)}. Activating rule-based fallback logic.")

        # Fallback to local predict_settlement_offer
        if not ai_success:
            logger.info(f"Executing predict_settlement_offer fallback for loan ID {loan_id}")
            fallback_res = predict_settlement_offer(user, loan)
            target_percentage = Decimal(str(fallback_res["recommended_settlement_percentage"]))
            risk = "High" if target_percentage < 50 else "Medium" if target_percentage < 70 else "Low"
            explanation = fallback_res["reasoning"]

        predicted_amount = (loan.outstanding_amount * (target_percentage / Decimal("100.00")))

        # Get DTI for risk score representation
        dti_score = profile.dti_ratio
        if dti_score > Decimal("1.0"):
            dti_score = dti_score / Decimal("100.0")

        # Save to database
        db_prediction = Settlement(
            loan_id=loan_id,
            suggested_settlement_percentage=target_percentage,
            risk_score=dti_score * Decimal("100.00"),
            risk_category=risk,
            final_offer_amount=predicted_amount
        )
        created_prediction = await self.repo.create(db, db_prediction)
        logger.info(f"AI Settlement Prediction ID {created_prediction.id} committed for loan ID {loan_id}")

        # Log audit trail
        audit_content = (
            f"Prediction ID: {created_prediction.id} | Loan ID: {loan_id} ({loan.lender_name}) | "
            f"Suggested Payout: {target_percentage:.2f}% | Amount: ${predicted_amount:.2f} | Risk: {risk} | "
            f"Rationale: {explanation}"
        )
        db_history = AIHistory(
            user_id=loan.user_id,
            query=prompt,
            response=audit_content
        )
        await self.history_repo.create(db, db_history)
        logger.info(f"AI history logged for user ID: {loan.user_id}")

        return created_prediction, explanation

# Global singleton instance
settlement_prediction_service = SettlementPredictionService()
