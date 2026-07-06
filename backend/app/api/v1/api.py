from fastapi import APIRouter
from app.auth.router import router as auth_router
from app.routers.user import router as user_router
from app.routers.loan import router as loan_router
from app.routers.financial_profile import router as profile_router
from app.routers.settlement_prediction import router as prediction_router
from app.routers.ai_negotiation import router as negotiation_router
from app.routers.ai_history import router as history_router

api_router = APIRouter()

# Register endpoints routers
api_router.include_router(auth_router)
api_router.include_router(user_router)
api_router.include_router(loan_router)
api_router.include_router(profile_router)
api_router.include_router(prediction_router)
api_router.include_router(negotiation_router)
api_router.include_router(history_router)






