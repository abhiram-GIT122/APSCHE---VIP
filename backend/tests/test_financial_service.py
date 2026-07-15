"""Unit tests for the financial calculation service."""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base, get_db
from app.models.user import User
from app.models.loan import Loan
from app.utils.auth import hash_password
from app.services.financial_service import calculate_financial_metrics

TEST_DATABASE_URL = "sqlite:///./test_finrelief.db"
engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


def get_test_db():
    db = TestSessionLocal()
    try:
        yield db
    finally:
        db.close()


def test_calculate_metrics_low_stress():
    db = next(get_test_db())
    user = User(
        email="test@test.com", username="testuser",
        hashed_password=hash_password("password"), monthly_income=100000,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    loan = Loan(
        user_id=user.id, lender_name="Test Bank", loan_type="personal",
        outstanding_amount=200000, monthly_emi=10000, overdue_duration_months=0,
    )
    db.add(loan)
    db.commit()

    metrics = calculate_financial_metrics(db, user)
    assert metrics["debt_stress_level"] == "LOW"
    assert metrics["emi_to_income_ratio"] == 10.0
    assert metrics["monthly_surplus"] == 90000
    db.close()


def test_calculate_metrics_high_stress():
    db = next(get_test_db())
    user = User(
        email="test2@test.com", username="testuser2",
        hashed_password=hash_password("password"), monthly_income=30000,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    loan = Loan(
        user_id=user.id, lender_name="Test Bank", loan_type="personal",
        outstanding_amount=500000, monthly_emi=20000, overdue_duration_months=6,
    )
    db.add(loan)
    db.commit()

    metrics = calculate_financial_metrics(db, user)
    assert metrics["debt_stress_level"] == "HIGH"
    assert metrics["emi_to_income_ratio"] > 60
    db.close()
