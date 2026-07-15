"""
Google Gemini AI Service for FinRelief AI
Handles: financial analysis, negotiation letters, settlement recommendations
"""
import json
import logging
from typing import Optional, Dict, Any

import google.generativeai as genai
from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

# Configure Gemini
genai.configure(api_key=settings.GEMINI_API_KEY)

try:
    model = genai.GenerativeModel(settings.GEMINI_MODEL_NAME)
except Exception as e:
    logger.warning(f"Gemini model initialization failed: {e}")
    model = None


# ---------- Prompt Templates ----------

NEGOTIATION_PROMPT = """You are a professional financial negotiator and legal advisor.
Generate a formal, professional negotiation letter to a lender for debt settlement.

Borrower Details:
- Name: {borrower_name}
- Monthly Income: ₹{monthly_income}
- Total Debt: ₹{total_debt}
- Loan Type: {loan_type}
- Outstanding Amount: ₹{outstanding_amount}
- Overdue Duration: {overdue_months} months
- Monthly EMI: ₹{emi}

Negotiation Type: {negotiation_type}
Proposed Settlement: ₹{proposed_settlement} ({settlement_percentage}%)

Requirements:
1. Professional formal letter format with date
2. Clear explanation of borrower's financial hardship
3. Specific settlement proposal with justification
4. Legal references to RBI guidelines on debt settlement (if India)
5. Request for written confirmation
6. Polite but firm tone

Generate the complete letter."""

FINANCIAL_ANALYSIS_PROMPT = """You are an expert financial analyst and debt counselor.
Analyze the following borrower's financial profile and provide actionable insights.

Financial Profile:
- Monthly Income: ₹{monthly_income}
- Total Debt: ₹{total_debt}
- Total Monthly EMI: ₹{total_emi}
- EMI-to-Income Ratio: {emi_ratio}%
- Monthly Surplus: ₹{surplus}
- Number of Active Loans: {num_loans}
- Debt Stress Level: {stress_level}

Provide a JSON response with:
{{
  "summary": "2-3 sentence overview",
  "risk_factors": ["list of risk factors"],
  "recommendations": ["actionable recommendations"],
  "debt_management_tips": ["specific tips"],
  "settlement_advice": "should they consider settlement?"
}}

Respond ONLY with valid JSON, no markdown formatting."""

SETTLEMENT_PROMPT = """You are an expert debt settlement advisor.
Given the following loan details, calculate and recommend an optimal settlement strategy.

Loan Details:
- Lender: {lender_name}
- Loan Type: {loan_type}
- Outstanding Amount: ₹{outstanding_amount}
- Monthly EMI: ₹{emi}
- Interest Rate: {interest_rate}%
- Overdue Duration: {overdue_months} months
- Borrower Monthly Income: ₹{monthly_income}
- Borrower Monthly Surplus: ₹{surplus}

Consider:
1. Industry-standard settlement ranges (40-70% of outstanding)
2. Borrower's repayment capacity
3. Overdue severity impact on negotiating power
4. RBI/Regulatory guidelines

Provide JSON response:
{{
  "recommended_settlement_amount": <number>,
  "settlement_percentage": <number>,
  "savings_amount": <number>,
  "rationale": "explanation",
  "risk_factors": ["list"],
  "repayment_plan_months": <number>,
  "confidence_level": "HIGH/MEDIUM/LOW"
}}

Respond ONLY with valid JSON."""


def generate_negotiation_letter(
    borrower_name: str,
    monthly_income: float,
    total_debt: float,
    loan_type: str,
    outstanding_amount: float,
    overdue_months: int,
    emi: float,
    negotiation_type: str,
    proposed_settlement: float,
) -> str:
    """Generate a professional negotiation letter using Gemini."""
    if model is None:
        return _fallback_negotiation_letter(borrower_name, negotiation_type, proposed_settlement)

    settlement_pct = (proposed_settlement / outstanding_amount * 100) if outstanding_amount else 0

    prompt = NEGOTIATION_PROMPT.format(
        borrower_name=borrower_name,
        monthly_income=monthly_income,
        total_debt=total_debt,
        loan_type=loan_type,
        outstanding_amount=outstanding_amount,
        overdue_months=overdue_months,
        emi=emi,
        negotiation_type=negotiation_type,
        proposed_settlement=proposed_settlement,
        settlement_percentage=f"{settlement_pct:.1f}",
    )

    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        logger.error(f"Gemini negotiation letter generation failed: {e}")
        return _fallback_negotiation_letter(borrower_name, negotiation_type, proposed_settlement)


def analyze_financial_profile(
    monthly_income: float,
    total_debt: float,
    total_emi: float,
    emi_ratio: float,
    surplus: float,
    num_loans: int,
    stress_level: str,
) -> Dict[str, Any]:
    """Analyze borrower's financial health using Gemini."""
    if model is None:
        return _fallback_financial_analysis(stress_level)

    prompt = FINANCIAL_ANALYSIS_PROMPT.format(
        monthly_income=monthly_income,
        total_debt=total_debt,
        total_emi=total_emi,
        emi_ratio=f"{emi_ratio:.1f}",
        surplus=surplus,
        num_loans=num_loans,
        stress_level=stress_level,
    )

    try:
        response = model.generate_content(prompt)
        text = response.text.strip()
        # Remove markdown code fences if present
        if text.startswith("```"):
            lines = text.split("\n")
            text = "\n".join(lines[1:-1] if lines[-1].strip() == "```" else lines[1:])
        return json.loads(text)
    except Exception as e:
        logger.error(f"Gemini financial analysis failed: {e}")
        return _fallback_financial_analysis(stress_level)


def generate_settlement_recommendation(
    lender_name: str,
    loan_type: str,
    outstanding_amount: float,
    emi: float,
    interest_rate: float,
    overdue_months: int,
    monthly_income: float,
    surplus: float,
) -> Dict[str, Any]:
    """Generate settlement recommendation using Gemini."""
    if model is None:
        return _fallback_settlement_recommendation(outstanding_amount)

    prompt = SETTLEMENT_PROMPT.format(
        lender_name=lender_name,
        loan_type=loan_type,
        outstanding_amount=outstanding_amount,
        emi=emi,
        interest_rate=interest_rate or 0,
        overdue_months=overdue_months,
        monthly_income=monthly_income,
        surplus=surplus,
    )

    try:
        response = model.generate_content(prompt)
        text = response.text.strip()
        if text.startswith("```"):
            lines = text.split("\n")
            text = "\n".join(lines[1:-1] if lines[-1].strip() == "```" else lines[1:])
        return json.loads(text)
    except Exception as e:
        logger.error(f"Gemini settlement recommendation failed: {e}")
        return _fallback_settlement_recommendation(outstanding_amount)


# ---------- Fallback Functions (when Gemini is unavailable) ----------

def _fallback_negotiation_letter(name: str, neg_type: str, amount: float) -> str:
    return f"""Date: {__import__('datetime').datetime.now().strftime('%d %B %Y')}

To,
The Manager / Recovery Department
[Lender Name]

Subject: Request for {neg_type.title()} of Loan Account

Dear Sir/Madam,

I, {name}, am writing to formally request a {neg_type} for my outstanding loan.
Due to unforeseen financial circumstances, I am currently facing difficulty in meeting
the full repayment obligation.

I propose a {neg_type} amount of Rs. {amount:,.2f} which I believe is a reasonable
and achievable figure given my current financial situation.

I request you to kindly consider this proposal and provide a written response
within 30 days as per RBI guidelines on fair practices.

Thank you for your understanding.

Yours faithfully,
{name}"""


def _fallback_financial_analysis(stress_level: str) -> Dict[str, Any]:
    return {
        "summary": f"Your debt stress level is {stress_level}. Immediate attention is recommended.",
        "risk_factors": ["High EMI burden", "Limited monthly surplus", "Risk of default"],
        "recommendations": [
            "Consider debt consolidation",
            "Explore settlement options with lenders",
            "Reduce discretionary spending",
        ],
        "debt_management_tips": [
            "Prioritize high-interest debts",
            "Build an emergency fund",
            "Avoid taking new loans",
        ],
        "settlement_advice": "Consider exploring settlement options given your current stress level.",
    }


def _fallback_settlement_recommendation(outstanding: float) -> Dict[str, Any]:
    recommended = outstanding * 0.55  # 55% as standard recommendation
    return {
        "recommended_settlement_amount": round(recommended, 2),
        "settlement_percentage": 55.0,
        "savings_amount": round(outstanding - recommended, 2),
        "rationale": f"Based on industry standards, a {55}% settlement is typically achievable for overdue accounts.",
        "risk_factors": ["Credit score impact", "Tax implications on waived amount"],
        "repayment_plan_months": 6,
        "confidence_level": "MEDIUM",
    }
