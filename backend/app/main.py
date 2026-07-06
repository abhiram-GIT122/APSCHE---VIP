import logging
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config.config import settings
from app.core.logging import setup_logging

from contextlib import asynccontextmanager
from app.database.session import engine
from app.models.base import Base
import app.models  # noqa

# Initialize Logging
setup_logging()
logger = logging.getLogger("app.main")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create tables on startup using async run_sync wrapper
    logger.info("Initializing database tables on startup...")
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database tables initialized successfully.")
    except Exception as e:
        logger.error(f"Startup database initialization failed: {e}")
    yield
    # Shutdown: clean up connection pool
    logger.info("Disposing database connection pool...")
    import asyncio
    try:
        await asyncio.shield(engine.dispose())
        logger.info("Database connection pool disposed.")
    except Exception as e:
        logger.error(f"Error during database connection pool disposal: {e}")

# Initialize FastAPI App
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Backend API for the AI-Powered Debt Relief & Financial Recovery Platform",
    version="1.0.0",
    openapi_url=f"{settings.API_V1_STR}/openapi.json" if settings.ENVIRONMENT != "production" else None,
    docs_url=f"{settings.API_V1_STR}/docs" if settings.ENVIRONMENT != "production" else None,
    redoc_url=f"{settings.API_V1_STR}/redoc" if settings.ENVIRONMENT != "production" else None,
    lifespan=lifespan,
)

# CORS Middleware Configuration
# Allows requests from localhost development servers (e.g. Vite React on http://localhost:5173)
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Custom Global Exception Handling
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """Handles HTTPExceptions (e.g. 404, 401) returning standard response body."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "data": None,
            "message": exc.detail
        }
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handles Pydantic payload validation exceptions."""
    errors_summary = "; ".join([f"{'.'.join(str(p) for p in err['loc'])}: {err['msg']}" for err in exc.errors()])
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "success": False,
            "data": None,
            "message": f"Validation failed: {errors_summary}"
        }
    )

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Logs unhandled exceptions and returns a structured 500 error response."""
    logger.error(
        f"Unhandled exception occurred. Request URL: {request.url.path} | Error: {str(exc)}",
        exc_info=True
    )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "data": None,
            "message": "An internal server error occurred. Please try again later."
        }
    )

# Basic Health Check Endpoint
@app.get("/", tags=["Health Check"])
async def health_check():
    """Simple API status endpoint for health monitoring."""
    logger.info("Health check endpoint invoked.")
    return {
        "success": True,
        "data": {"status": "healthy"},
        "message": "FinRelief AI Backend Running"
    }

# Register API Router orchestrator
from app.api.v1.api import api_router
app.include_router(api_router, prefix=settings.API_V1_STR)

