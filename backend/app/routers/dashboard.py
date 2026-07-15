"""Dashboard routes: financial health overview and AI insights."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.models.loan import Loan
from app.models.financial_profile import FinancialProfile
from app.models.negotiation import NegotiationHistory
from app.models.settlement import SettlementRecommendation
from app.schemas.financial import FinancialProfileResponse, FinancialAnalysis
from app.utils.auth import get_current_user
from app.services.financial_service import calculate_financial_metrics, update_financial_profile
from app.services.ai_service import analyze_financial_profile

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])


@router.get("/overview")
def get_dashboard_overview(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get complete dashboard data: profile, loans, negotiations, settlements."""
    # Calculate and update metrics
    metrics = calculate_financial_metrics(db, current_user)
    profile = update_financial_profile(db, current_user, metrics)

    active_loans = db.query(Loan).filter(
        Loan.user_id == current_user.id, Loan.is_active == True
    ).all()

    recent_negotiations = db.query(NegotiationHistory).filter(
        NegotiationHistory.user_id == current_user.id
    ).order_by(NegotiationHistory.created_at.desc()).limit(5).all()

    recent_settlements = db.query(SettlementRecommendation).filter(
        SettlementRecommendation.user_id == current_user.id
    ).order_by(SettlementRecommendation.created_at.desc()).limit(5).all()

    return {
        "user": {
            "id": current_user.id,
            "username": current_user.username,
            "full_name": current_user.full_name,
            "monthly_income": current_user.monthly_income,
        },
        "financial_profile": FinancialProfileResponse.model_validate(profile),
        "summary": metrics,
        "active_loans_count": len(active_loans),
        "loans": [
            {
                "id": l.id,
                "lender_name": l.lender_name,
                "loan_type": l.loan_type,
                "outstanding_amount": l.outstanding_amount,
                "monthly_emi": l.monthly_emi,
                "overdue_months": l.overdue_duration_months,
            }
            for l in active_loans
        ],
        "recent_negotiations": [
            {
                "id": n.id,
                "lender": n.lender_name,
                "type": n.negotiation_type,
                "status": n.status,
                "amount": n.proposed_settlement_amount,
            }
            for n in recent_negotiations
        ],
        "recent_settlements": [
            {
                "id": s.id,
                "loan_id": s.loan_id,
                "recommended_amount": s.recommended_settlement_amount,
                "savings": s.savings_amount,
                "percentage": s.settlement_percentage,
            }
            for s in recent_settlements
        ],
    }


@router.get("/ai-insights")
def get_ai_insights(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get AI-generated financial health insights."""
    metrics = calculate_financial_metrics(db, current_user)

    insights = analyze_financial_profile(
        monthly_income=metrics["monthly_income"],
        total_debt=metrics["total_debt"],
        total_emi=metrics["total_emi"],
        emi_ratio=metrics["emi_to_income_ratio"],
        surplus=metrics["monthly_surplus"],
        num_loans=metrics["num_active_loans"],
        stress_level=metrics["debt_stress_level"],
    )

    # Store insights in profile
    profile = db.query(FinancialProfile).filter(FinancialProfile.user_id == current_user.id).first()
    if profile:
        profile.ai_insights = insights
        db.commit()

    return {"insights": insights, "metrics": metrics}
