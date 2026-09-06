"""
FastAPI Security & Authentication Dependencies.
Provides JWT token extraction, user validation, and Role-Based Access Control (RBAC).
"""

from typing import List, Optional
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from app.core.security import JWTHandler, SecurityException
from app.schemas.auth import AuditEventType, UserRecord, UserRole
from app.security.audit_logger import audit_logger
from app.security.user_store import user_store
from app.utils.logger import logger

# HTTP Bearer scheme (auto_error=False allows optional auth for non-breaking progressive migration)
bearer_scheme = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme)
) -> UserRecord:
    """
    Dependency that enforces valid JWT Bearer token authentication.
    Returns the authenticated UserRecord.
    """
    if not credentials or not credentials.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required. Please provide a valid Bearer token.",
            headers={"WWW-Authenticate": "Bearer"}
        )

    token = credentials.credentials
    try:
        payload = JWTHandler.decode_access_token(token)
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token payload missing subject identifier.",
                headers={"WWW-Authenticate": "Bearer"}
            )

        user = user_store.get_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User account associated with token not found.",
                headers={"WWW-Authenticate": "Bearer"}
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is deactivated."
            )

        return user

    except SecurityException as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
            headers={"WWW-Authenticate": "Bearer"}
        )
    except HTTPException:
        raise
    except Exception as exc:
        logger.error(f"Unexpected authentication error: {exc}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication verification failed.",
            headers={"WWW-Authenticate": "Bearer"}
        )


async def get_optional_current_user(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme)
) -> Optional[UserRecord]:
    """
    Dependency for routes where authentication is optional.
    Returns UserRecord if a valid token is provided, or None if anonymous.
    """
    if not credentials or not credentials.credentials:
        return None

    try:
        payload = JWTHandler.decode_access_token(credentials.credentials)
        user_id = payload.get("sub")
        if user_id:
            return user_store.get_by_id(user_id)
    except Exception:
        # Ignore decoding errors for optional routes
        return None
    return None


def require_role(allowed_roles: List[UserRole]):
    """
    Dependency factory to enforce Role-Based Access Control (RBAC).
    """
    async def role_checker(
        request: Request,
        current_user: UserRecord = Depends(get_current_user)
    ) -> UserRecord:
        user_role = current_user.role
        if isinstance(user_role, str):
            try:
                user_role = UserRole(user_role)
            except ValueError:
                pass

        if user_role not in allowed_roles:
            client_ip = request.client.host if request.client else "127.0.0.1"
            audit_logger.log_event(
                event_type=AuditEventType.ACCESS_DENIED,
                user_id=current_user.id,
                username=current_user.username,
                role=str(current_user.role.value if hasattr(current_user.role, 'value') else current_user.role),
                ip_address=client_ip,
                status="FAILURE",
                target_resource=request.url.path,
                metadata={
                    "required_roles": [r.value for r in allowed_roles],
                    "user_role": str(current_user.role.value if hasattr(current_user.role, 'value') else current_user.role)
                }
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Requires one of roles: {[r.value for r in allowed_roles]}"
            )
        return current_user

    return role_checker


# Convenient role shortcut dependencies
require_admin = require_role([UserRole.ADMIN])
require_developer = require_role([UserRole.DEVELOPER, UserRole.ADMIN])
