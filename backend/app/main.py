"""
FinRelief AI - FastAPI Application Entry Point
The AI-Powered Debt Relief & Financial Recovery Platform
"""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.database import engine, Base

# Import models so they are registered with Base metadata
from app.models import user, loan, financial_profile, negotiation_model, settlement_model  # noqa: F401

from app.routers import auth, loans, dashboard
from app.routers import negotiation as negotiation_router
from app.routers import settlement as settlement_router

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("finrelief")

settings = get_settings()


# ---------- Lifespan: create tables on startup ----------
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Creating database tables if they don't exist...")
    Base.metadata.create_all(bind=engine)
    logger.info("FinRelief AI is ready!")
    yield
    logger.info("Shutting down FinRelief AI...")


# ---------- FastAPI App ----------
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="AI-Powered Debt Relief & Financial Recovery Platform",
    lifespan=lifespan,
)

# ---------- CORS ----------
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------- Routes ----------
app.include_router(auth.router)
app.include_router(loans.router)
app.include_router(dashboard.router)
app.include_router(negotiation_router.router)
app.include_router(settlement_router.router)


# ---------- Root ----------
@app.get("/")
def root():
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
        "docs": "/docs",
    }


@app.get("/health")
def health_check():
    return {"status": "healthy"}
