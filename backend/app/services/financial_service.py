"""
Financial calculation and analysis service.
Computes financial health metrics for borrowers.
"""
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from app.models.loan import Loan
from app.models.user import User
from app.models.financial_profile import FinancialProfile


def calculate_financial_metrics(db: Session, user: User) -> Dict[str, Any]:
    """Calculate all financial health metrics for a user."""
    active_loans = db.query(Loan).filter(
        Loan.user_id == user.id,
        Loan.is_active == True
    ).all()

    total_debt = sum(loan.outstanding_amount for loan in active_loans)
    total_emi = sum(loan.monthly_emi for loan in active_loans)
    monthly_income = user.monthly_income or 0

    emi_ratio = (total_emi / monthly_income * 100) if monthly_income > 0 else 0
    monthly_surplus = monthly_income - total_emi

    # Determine debt stress level
    if emi_ratio <= 20:
        stress_level = "LOW"
    elif emi_ratio <= 40:
        stress_level = "MODERATE"
    elif emi_ratio <= 60:
        stress_level = "HIGH"
    else:
        stress_level = "CRITICAL"

    # Estimate credit score (simplified)
    credit_score = _estimate_credit_score(db, user, emi_ratio, active_loans)

    # Settlement readiness
    readiness = _calculate_settlement_readiness(db, user, active_loans)

    return {
        "total_debt": round(total_debt, 2),
        "total_emi": round(total_emi, 2),
        "emi_to_income_ratio": round(emi_ratio, 2),
        "monthly_surplus": round(monthly_surplus, 2),
        "debt_stress_level": stress_level,
        "credit_score_estimate": credit_score,
        "settlement_readiness_score": round(readiness, 2),
        "num_active_loans": len(active_loans),
        "monthly_income": monthly_income,
    }


def update_financial_profile(db: Session, user: User, metrics: Dict[str, Any]) -> FinancialProfile:
    """Create or update the user's financial profile."""
    profile = db.query(FinancialProfile).filter(FinancialProfile.user_id == user.id).first()

    if profile:
        profile.total_debt = metrics["total_debt"]
        profile.total_emi = metrics["total_emi"]
        profile.emi_to_income_ratio = metrics["emi_to_income_ratio"]
        profile.monthly_surplus = metrics["monthly_surplus"]
        profile.debt_stress_level = metrics["debt_stress_level"]
        profile.credit_score_estimate = metrics["credit_score_estimate"]
        profile.settlement_readiness_score = metrics["settlement_readiness_score"]
    else:
        profile = FinancialProfile(
            user_id=user.id,
            total_debt=metrics["total_debt"],
            total_emi=metrics["total_emi"],
            emi_to_income_ratio=metrics["emi_to_income_ratio"],
            monthly_surplus=metrics["monthly_surplus"],
            debt_stress_level=metrics["debt_stress_level"],
            credit_score_estimate=metrics["credit_score_estimate"],
            settlement_readiness_score=metrics["settlement_readiness_score"],
        )
        db.add(profile)

    db.commit()
    db.refresh(profile)
    return profile


def _estimate_credit_score(db: Session, user: User, emi_ratio: float, loans: List[Loan]) -> int:
    """Simplified credit score estimation based on financial metrics."""
    base_score = 750

    # Penalize for high EMI ratio
    if emi_ratio > 60:
        base_score -= 150
    elif emi_ratio > 40:
        base_score -= 100
    elif emi_ratio > 20:
        base_score -= 50

    # Penalize for overdue loans
    total_overdue = sum(loan.overdue_duration_months for loan in loans)
    if total_overdue > 12:
        base_score -= 150
    elif total_overdue > 6:
        base_score -= 100
    elif total_overdue > 3:
        base_score -= 50

    # Penalize for high debt-to-loan ratio
    num_loans = len(loans)
    if num_loans > 5:
        base_score -= 50

    return max(300, min(900, base_score))


def _calculate_settlement_readiness(db: Session, user: User, loans: List[Loan]) -> float:
    """Calculate how suitable the borrower is for settlement (0-100)."""
    score = 50.0

    avg_overdue = sum(loan.overdue_duration_months for loan in loans) / max(len(loans), 1)
    if avg_overdue > 6:
        score += 20
    elif avg_overdue > 3:
        score += 10

    total_debt = sum(loan.outstanding_amount for loan in loans)
    if total_debt > 500000:
        score += 10

    if user.monthly_income and user.monthly_income < total_debt * 0.5:
        score += 10

    return min(100, max(0, score))
