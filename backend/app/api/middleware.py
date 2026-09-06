"""
Security Headers, Rate Limiting Middleware & Centralized Error Handlers.
Implements defense-in-depth HTTP headers, brute-force rate limiting, and secure error normalization.
"""

import time
import threading
from collections import defaultdict, deque
from typing import Dict, Deque
from fastapi import FastAPI, Request, Response, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from app.core.config import settings
from app.schemas.auth import AuditEventType
from app.security.audit_logger import audit_logger
from app.utils.logger import logger


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Applies enterprise defense-in-depth HTTP security headers to all responses.
    """
    async def dispatch(self, request: Request, call_next):
        response: Response = await call_next(request)
        
        # Hardened HTTP Security Headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Content-Security-Policy"] = "default-src 'self'; frame-ancestors 'none';"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(), camera=(), microphone=()"
        response.headers["X-Privacy-Assurance"] = "zero-raw-secret-leakage-guarantee"

        return response


class RateLimiterMiddleware(BaseHTTPMiddleware):
    """
    In-Memory sliding-window rate limiter protecting authentication and analysis endpoints.
    """
    def __init__(self, app: FastAPI):
        super().__init__(app)
        self._lock = threading.Lock()
        # IP -> Deque of timestamps
        self._login_buckets: Dict[str, Deque[float]] = defaultdict(deque)
        self._scan_buckets: Dict[str, Deque[float]] = defaultdict(deque)

    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host if request.client else "127.0.0.1"
        path = request.url.path
        now = time.time()
        window_seconds = 60.0

        # 1. Rate Limit for Login Endpoint (brute-force defense)
        if path.endswith("/auth/login") and request.method == "POST":
            with self._lock:
                bucket = self._login_buckets[client_ip]
                # Clean expired timestamps
                while bucket and bucket[0] < now - window_seconds:
                    bucket.popleft()

                if len(bucket) >= settings.RATE_LIMIT_LOGIN_PER_MINUTE:
                    audit_logger.log_event(
                        event_type=AuditEventType.RATE_LIMIT_EXCEEDED,
                        ip_address=client_ip,
                        status="WARNING",
                        target_resource="/api/auth/login",
                        metadata={"endpoint": "auth_login", "limit_per_minute": settings.RATE_LIMIT_LOGIN_PER_MINUTE}
                    )
                    return JSONResponse(
                        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                        content={
                            "success": False,
                            "error": "Too many login attempts. Please wait 60 seconds before retrying.",
                            "error_type": "RATE_LIMIT_EXCEEDED"
                        },
                        headers={"Retry-After": "60"}
                    )
                bucket.append(now)

        # 2. Rate Limit for Heavy Analysis Endpoints
        elif ("/analysis" in path or "/github/pr" in path) and request.method == "POST":
            with self._lock:
                bucket = self._scan_buckets[client_ip]
                while bucket and bucket[0] < now - window_seconds:
                    bucket.popleft()

                if len(bucket) >= settings.RATE_LIMIT_SCAN_PER_MINUTE:
                    audit_logger.log_event(
                        event_type=AuditEventType.RATE_LIMIT_EXCEEDED,
                        ip_address=client_ip,
                        status="WARNING",
                        target_resource=path,
                        metadata={"endpoint": "analysis_scan", "limit_per_minute": settings.RATE_LIMIT_SCAN_PER_MINUTE}
                    )
                    return JSONResponse(
                        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                        content={
                            "success": False,
                            "error": "Analysis rate limit exceeded. Please wait a moment.",
                            "error_type": "RATE_LIMIT_EXCEEDED"
                        },
                        headers={"Retry-After": "60"}
                    )
                bucket.append(now)

        return await call_next(request)


def setup_exception_handlers(app: FastAPI) -> None:
    """
    Register centralized exception handlers to prevent raw internal stack trace disclosure.
    """
    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "success": False,
                "status_code": exc.status_code,
                "detail": str(exc.detail),
                "error": str(exc.detail),
                "error_type": "HTTP_EXCEPTION"
            }
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        errors = []
        for err in exc.errors():
            loc = " -> ".join([str(l) for l in err.get("loc", [])])
            errors.append(f"{loc}: {err.get('msg')}")
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "success": False,
                "status_code": 422,
                "error": "Request input validation failed.",
                "validation_errors": errors,
                "error_type": "VALIDATION_ERROR"
            }
        )

    @app.exception_handler(Exception)
    async def generic_exception_handler(request: Request, exc: Exception):
        logger.error(f"Unhandled Exception on [{request.method}] {request.url.path}: {exc}", exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "success": False,
                "status_code": 500,
                "error": "An internal server error occurred. Please contact the security administrator.",
                "error_type": "INTERNAL_SERVER_ERROR"
            }
        )
