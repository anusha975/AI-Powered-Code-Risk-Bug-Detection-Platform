"""
Authentication API Router.
Handles user registration, secure login with PBKDF2 verification, JWT issuance, and profile retrieval.
"""

from fastapi import APIRouter, Depends, HTTPException, Request, status
from app.core.config import settings
from app.core.security import JWTHandler, PasswordHasher
from app.api.deps import get_current_user
from app.schemas.auth import (
    AuditEventType,
    TokenResponse,
    UserLoginRequest,
    UserProfileResponse,
    UserRecord,
    UserRegisterRequest
)
from app.security.audit_logger import audit_logger
from app.security.user_store import user_store
from app.utils.logger import logger

router = APIRouter(prefix="/auth", tags=["Authentication & Authorization"])


@router.post(
    "/register",
    response_model=UserProfileResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new platform user"
)
async def register(request: Request, payload: UserRegisterRequest):
    """
    Register a new user with secure password hashing and role assignment.
    """
    client_ip = request.client.host if request.client else "127.0.0.1"

    try:
        user = user_store.create_user(
            username=payload.username,
            email=payload.email,
            plain_password=payload.password,
            role=payload.role
        )

        # Log security audit event (zero password/credential leakage)
        audit_logger.log_event(
            event_type=AuditEventType.USER_REGISTERED,
            user_id=user.id,
            username=user.username,
            role=user.role.value if hasattr(user.role, 'value') else str(user.role),
            ip_address=client_ip,
            status="SUCCESS",
            target_resource="/api/auth/register",
            metadata={"email": user.email, "role": user.role.value if hasattr(user.role, 'value') else str(user.role)}
        )

        return UserProfileResponse(
            id=user.id,
            username=user.username,
            email=user.email,
            role=user.role,
            is_active=user.is_active,
            created_at=user.created_at,
            last_login_at=user.last_login_at
        )

    except ValueError as exc:
        audit_logger.log_event(
            event_type=AuditEventType.USER_REGISTERED,
            ip_address=client_ip,
            status="FAILURE",
            target_resource="/api/auth/register",
            metadata={"attempted_username": payload.username, "error": str(exc)}
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc)
        )


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Authenticate and receive JWT token"
)
async def login(request: Request, payload: UserLoginRequest):
    """
    Authenticate user credentials using PBKDF2-HMAC constant-time comparison and return signed JWT token.
    """
    client_ip = request.client.host if request.client else "127.0.0.1"
    user = user_store.get_by_username_or_email(payload.username_or_email)

    if not user or not PasswordHasher.verify_password(payload.password, user.hashed_password):
        audit_logger.log_event(
            event_type=AuditEventType.LOGIN_FAILURE,
            ip_address=client_ip,
            status="FAILURE",
            target_resource="/api/auth/login",
            metadata={"attempted_identifier": payload.username_or_email[:30]}
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password.",
            headers={"WWW-Authenticate": "Bearer"}
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is inactive or disabled."
        )

    # Update login timestamp
    user_store.update_last_login(user.id)

    # Generate JWT access token
    role_str = user.role.value if hasattr(user.role, 'value') else str(user.role)
    token = JWTHandler.create_access_token(
        subject=user.id,
        claims={
            "username": user.username,
            "role": role_str,
            "email": user.email
        }
    )

    # Log successful authentication
    audit_logger.log_event(
        event_type=AuditEventType.LOGIN_SUCCESS,
        user_id=user.id,
        username=user.username,
        role=role_str,
        ip_address=client_ip,
        status="SUCCESS",
        target_resource="/api/auth/login",
        metadata={"auth_scheme": "JWT_BEARER"}
    )

    profile = UserProfileResponse(
        id=user.id,
        username=user.username,
        email=user.email,
        role=user.role,
        is_active=user.is_active,
        created_at=user.created_at,
        last_login_at=user.last_login_at
    )

    return TokenResponse(
        access_token=token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user=profile
    )


@router.get(
    "/me",
    response_model=UserProfileResponse,
    summary="Get current authenticated user profile"
)
async def get_me(current_user: UserRecord = Depends(get_current_user)):
    """
    Retrieve sanitized profile for the current authenticated user.
    """
    return UserProfileResponse(
        id=current_user.id,
        username=current_user.username,
        email=current_user.email,
        role=current_user.role,
        is_active=current_user.is_active,
        created_at=current_user.created_at,
        last_login_at=current_user.last_login_at
    )
