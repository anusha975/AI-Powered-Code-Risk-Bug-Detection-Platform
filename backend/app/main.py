"""
Privacy-Preserving AI Code Security & Risk Analysis Platform
FastAPI Application Entry Point.
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.core.config import settings
from app.api.router import api_router
from app.database.base import Base
from app.database.session import engine
from app.utils.logger import logger


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Application lifespan manager for startup and shutdown events.
    """
    logger.info(f"Starting {settings.APP_NAME} (v{settings.APP_VERSION}) in [{settings.ENVIRONMENT}] mode.")
    logger.info(f"Privacy Policy Enforcement: Analysis Mode = [{settings.ANALYSIS_MODE.value}]")
    
    # Attempt to initialize database tables if database is available
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database schema validated and ready.")
    except Exception as exc:
        logger.warning(f"Database table initialization skipped (DB offline or unreachable): {exc}")
        
    yield
    
    logger.info(f"Shutting down {settings.APP_NAME} gracefully.")


def create_application() -> FastAPI:
    """FastAPI Application Factory."""
    application = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description=(
            "A privacy-first security and risk analysis platform for source code. "
            "Guarantees local static analysis, secret redaction, context minimization, "
            "and zero unauthorized remote code transmission."
        ),
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url=f"{settings.API_PREFIX}/openapi.json",
        lifespan=lifespan
    )

    # Configure CORS Middleware
    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS if isinstance(settings.CORS_ORIGINS, list) else ["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Attach Module 12 Security Headers and Rate Limiter Middlewares
    from app.api.middleware import RateLimiterMiddleware, SecurityHeadersMiddleware, setup_exception_handlers
    application.add_middleware(SecurityHeadersMiddleware)
    application.add_middleware(RateLimiterMiddleware)

    # Configure Centralized Exception Handlers
    setup_exception_handlers(application)

    # Mount API Router under prefix (e.g. /api)
    application.include_router(api_router, prefix=settings.API_PREFIX)

    @application.get("/", tags=["Root"])
    def root_status() -> JSONResponse:
        """Root landing endpoint."""
        return JSONResponse(
            content={
                "app": settings.APP_NAME,
                "version": settings.APP_VERSION,
                "status": "OPERATIONAL",
                "docs_url": "/docs",
                "health_endpoint": f"{settings.API_PREFIX}/health",
                "privacy_mode": settings.ANALYSIS_MODE.value
            }
        )

    return application


app = create_application()
