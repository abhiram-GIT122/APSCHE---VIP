import logging
from datetime import datetime
from decimal import Decimal
from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.models.loan import Loan
from app.models.financial_profile import FinancialProfile
from app.models.settlement import Settlement
from app.models.ai_negotiation import AINegotiation
from app.models.ai_history import AIHistory
from app.schemas.ai_negotiation import AINegotiationCreate
from app.repositories.ai_negotiation import AINegotiationRepository, ai_negotiation_repository
from app.repositories.loan import LoanRepository, loan_repository
from app.repositories.financial_profile import FinancialProfileRepository, financial_profile_repository
from app.repositories.ai_history import AIHistoryRepository, ai_history_repository
from app.repositories.settlement_prediction import settlement_prediction_repository
from app.repositories.user import user_repository
from app.ai.client import GeminiClient, gemini_client

logger = logging.getLogger("app.services.ai_negotiation_service")

def generate_negotiation_strategy(
    user_profile: FinancialProfile,
    loan_summary: Dict[str, Any],
    settlement_data: Dict[str, Any]
) -> Dict[str, Any]:
    """Generates negotiation strategy message, tone, and key points based on DTI risk levels.
    
    Tones based on risk level:
    - HIGH risk (DTI > 0.5) -> urgent
    - MEDIUM risk (0.3 <= DTI <= 0.5) -> balanced
    - LOW risk (DTI < 0.3) -> confident
    """
    # 1. Determine risk level and tone
    risk_level = str(settlement_data.get("risk_level") or "LOW").upper()
    
    # Normalize DTI for fallback checks
    dti = user_profile.dti_ratio
    if dti > Decimal("1.0"):
        dti = dti / Decimal("100.0")

    if risk_level == "HIGH" or dti > Decimal("0.5"):
        tone = "urgent"
        key_points = [
            "Severe financial hardship and budget constraints",
            "Imminent risk of payment default and insolvency",
            "Request for aggressive settlement write-off to close liability"
        ]
    elif risk_level == "MEDIUM" or dti >= Decimal("0.3"):
        tone = "balanced"
        key_points = [
            "Mutually beneficial lump-sum clearance proposal",
            "Limited cash surplus allocated for settlement payout",
            "Restructuring options to settle account balance"
        ]
    else:
        tone = "confident"
        key_points = [
            "Clear capacity for immediate lump-sum settlement payment",
            "Resolution proposal aimed at closing the target liability",
            "Standard repayment optimization terms"
        ]

    # Calculate default text parameters
    total_loan = loan_summary.get("total_loan_amount", 0.0)
    offer = settlement_data.get("settlement_amount", 0.0)
    percentage = settlement_data.get("settlement_percentage", 50.0)

    # 2. Formulate negotiation message
    if tone == "urgent":
        message = (
            f"Dear Collections Manager,\n\n"
            f"I am writing to propose an urgent hardship settlement regarding my outstanding debt balance. "
            f"Due to severe financial hardship (DTI ratio of {dti*100:.2f}%), I am experiencing extreme budget constraints. "
            f"I request that we agree to settle the balance for an aggressive settlement amount of ${offer:.2f} "
            f"({percentage:.2f}% of the total ${total_loan:.2f} balance) to resolve this account permanently."
        )
    elif tone == "balanced":
        message = (
            f"Dear Accounts Manager,\n\n"
            f"I am contacting you to propose a balanced settlement negotiation to resolve my outstanding balance. "
            f"Based on my current financial assessment, I would like to propose a moderate settlement of ${offer:.2f} "
            f"({percentage:.2f}% of the total ${total_loan:.2f} balance). This proposal offers a mutually beneficial resolution "
            f"and provides stable restructuring options."
        )
    else:
        message = (
            f"Dear Credit Representative,\n\n"
            f"I am writing to propose a standard repayment optimization to close out my account. "
            f"With my stable financial profile (DTI ratio of {dti*100:.2f}%), I am prepared to clear the outstanding balance "
            f"by offering a payment of ${offer:.2f} ({percentage:.2f}% of the total ${total_loan:.2f} balance). "
            f"I look forward to your agreement to initiate a prompt payment."
        )

    return {
        "tone": tone,
        "message": message,
        "key_points": key_points
    }

class AINegotiationService:
    """Manages business operations coordinates for drafting custom hardship proposal letters with Gemini."""
    
    def __init__(
        self,
        repo: AINegotiationRepository = ai_negotiation_repository,
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

    async def get_negotiations_by_loan(self, db: AsyncSession, loan_id: int) -> List[AINegotiation]:
        """Fetch all negotiations linked to a specific loan."""
        return await self.repo.get_by_loan_id(db, loan_id)

    async def get_negotiations_by_user(self, db: AsyncSession, user_id: int) -> List[AINegotiation]:
        """Fetch all negotiations linked to a specific user."""
        return await self.repo.get_by_user_id(db, user_id)

    async def generate_negotiation_letter(self, db: AsyncSession, user_id: int, request_in: AINegotiationCreate) -> Optional[AINegotiation]:
        """Formulates the negotiation prompt, queries Gemini, saves the letter, and logs transactions."""
        loan = await self.loan_repo.get_by_id(db, request_in.loan_id)
        if not loan or loan.user_id != user_id:
            logger.warning(f"Letter generate failed: Loan ID {request_in.loan_id} not found or unauthorized")
            return None

        profile = await self.profile_repo.get_by_user_id(db, user_id)
        if not profile:
            logger.warning(f"Letter generate failed: Profile not found for User ID {user_id}")
            return None

        # Fetch latest prediction
        predictions = await settlement_prediction_repository.get_by_loan_id(db, request_in.loan_id)
        latest_prediction = predictions[-1] if predictions else None
        
        if latest_prediction:
            recommended_offer = latest_prediction.final_offer_amount
            suggested_percentage = latest_prediction.suggested_settlement_percentage
        else:
            recommended_offer = loan.outstanding_amount * Decimal("0.50")
            suggested_percentage = Decimal("50.00")

        # Fallback prediction mock if latest_prediction was absent
        mock_prediction = latest_prediction or Settlement(
            loan_id=loan.id,
            suggested_settlement_percentage=suggested_percentage,
            risk_score=Decimal("0.00"),
            risk_category="Medium",
            final_offer_amount=recommended_offer
        )

        # Fetch loan summary and prepare settlement data
        from app.services.loan import loan_service
        loan_summary = await loan_service.get_user_loan_summary(db, user_id)
        
        settlement_data = {
            "risk_level": str(mock_prediction.risk_category or "MEDIUM").upper(),
            "settlement_percentage": float(suggested_percentage),
            "settlement_amount": float(recommended_offer),
            "reasoning": "Standard prediction input parameters."
        }

        # Call modular negotiation strategy builder helper
        strategy_res = generate_negotiation_strategy(profile, loan_summary, settlement_data)

        # 4. Try calling Google Gemini AI
        letter_content = ""
        explanation = ""
        ai_success = False

        prompt = (
            f"Draft a formal, professional debt negotiation letter on behalf of a debtor to their lender.\n"
            f"Lender Name: {loan.lender_name}\n"
            f"Debt Balance Owed: ${loan.outstanding_amount:.2f}\n"
            f"Chosen Strategy: {request_in.negotiation_strategy}\n"
            f"Recommended Settlement Offer: ${recommended_offer:.2f} ({suggested_percentage:.2f}% of total)\n"
            f"Debtor Financial Parameters:\n"
            f"- Stress level: {profile.stress_level}\n"
            f"- Preselected Tone: {strategy_res['tone']}\n"
            f"- Preselected Key Points: {', '.join(strategy_res['key_points'])}\n\n"
            f"Please structure the draft using standard professional letter fields, and write a custom letter in the indicated tone."
        )

        if self.ai_client.api_key:
            try:
                letter_content = await self.ai_client.generate_negotiation_letter(prompt)
                explanation = f"AI Negotiation letter generated using Gemini API with tone: '{strategy_res['tone']}'."
                ai_success = True
                logger.info(f"Gemini API generated negotiation letter for loan ID {request_in.loan_id}.")
            except Exception as exc:
                logger.warning(f"Gemini API letter generation failed: {str(exc)}. Activating rule-based fallback letter.")

        if not ai_success:
            logger.info("Executing rule-based fallback negotiation letter generation.")
            letter_content = strategy_res["message"]
            explanation = f"Rule-based Fallback: Generated negotiation letter using local strategy template. Tone: '{strategy_res['tone']}'."

        # Save model instance to Database
        db_negotiation = AINegotiation(
            loan_id=request_in.loan_id,
            generated_letter=letter_content,
            model_used=request_in.negotiation_strategy
        )
        created_negotiation = await self.repo.create(db, db_negotiation)
        logger.info(f"AI Negotiation letter ID {created_negotiation.id} created for loan ID {request_in.loan_id}")

        # Log transaction to Audit trail (AIHistory)
        audit_content = (
            f"Negotiation ID: {created_negotiation.id} | Loan ID: {request_in.loan_id} ({loan.lender_name}) | "
            f"Strategy: {request_in.negotiation_strategy} | Tone: {strategy_res['tone']} | "
            f"Source: {'Gemini API' if ai_success else 'Rule-based Fallback'}"
        )
        db_history = AIHistory(
            user_id=user_id,
            query=prompt,
            response=audit_content
        )
        await self.history_repo.create(db, db_history)
        logger.info(f"AI history logged for user ID: {user_id}")

        # Attach dynamic fields for router serialization
        created_negotiation.recommended_offer = recommended_offer
        created_negotiation.explanation = explanation

        return created_negotiation

# Global singleton instance
ai_negotiation_service = AINegotiationService()
