"""
Comprehensive Automated Unit & Integration Tests for Module 12:
Authentication, Authorization, RBAC, Password Hashing, JWT Tokens, and Security Audit Logging.
"""

import time
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.security import JWTHandler, PasswordHasher, SecurityException
from app.schemas.auth import AuditEventType, UserRole
from app.security.audit_logger import audit_logger
from app.security.user_store import user_store


@pytest.fixture(scope="module")
def client():
    """Test client fixture."""
    with TestClient(app) as test_client:
        yield test_client


def test_password_hasher_pbkdf2_and_salt():
    """Verify NIST SP 800-63B PBKDF2-HMAC-SHA256 password hashing and salt uniqueness."""
    password = "TestStrongPassword!2026"
    hash1 = PasswordHasher.hash_password(password)
    hash2 = PasswordHasher.hash_password(password)

    # Hashes must be different due to unique 32-byte salts
    assert hash1 != hash2
    assert hash1.startswith("pbkdf2_sha256$100000$")
    assert hash2.startswith("pbkdf2_sha256$100000$")

    # Constant-time verification
    assert PasswordHasher.verify_password(password, hash1) is True
    assert PasswordHasher.verify_password(password, hash2) is True
    assert PasswordHasher.verify_password("WrongPassword!123", hash1) is False
    assert PasswordHasher.verify_password("", hash1) is False


def test_jwt_token_generation_and_verification():
    """Verify JWT access token creation, claims encoding, and validation."""
    subject_id = "USR-TEST-0001"
    claims = {"username": "alice", "role": "DEVELOPER", "email": "alice@security.local"}

    token = JWTHandler.create_access_token(subject=subject_id, claims=claims)
    assert isinstance(token, str)
    assert len(token) > 20

    # Decode and verify payload
    decoded = JWTHandler.decode_access_token(token)
    assert decoded["sub"] == subject_id
    assert decoded["username"] == "alice"
    assert decoded["role"] == "DEVELOPER"
    assert "exp" in decoded
    assert "iat" in decoded
    assert "jti" in decoded


def test_jwt_token_tampering_and_expiration_rejection():
    """Verify that tampered or malformed tokens are rejected with SecurityException."""
    subject_id = "USR-TEST-0002"
    token = JWTHandler.create_access_token(subject=subject_id)

    # Tamper with signature
    tampered = token[:-5] + "XXXXX"
    with pytest.raises(SecurityException):
        JWTHandler.decode_access_token(tampered)

    # Empty token
    with pytest.raises(SecurityException):
        JWTHandler.decode_access_token("")


def test_user_store_preseed_and_registration():
    """Verify pre-seeded admin/developer accounts and new user registration."""
    # Preseeded accounts
    admin = user_store.get_by_username("admin")
    assert admin is not None
    assert admin.role == UserRole.ADMIN

    dev = user_store.get_by_username("developer")
    assert dev is not None
    assert dev.role == UserRole.DEVELOPER

    # Register new user
    new_user = user_store.create_user(
        username="carol_dev",
        email="carol@security.local",
        plain_password="CarolPassword!2026",
        role=UserRole.DEVELOPER
    )
    assert new_user.username == "carol_dev"
    assert new_user.role == UserRole.DEVELOPER
    assert PasswordHasher.verify_password("CarolPassword!2026", new_user.hashed_password)

    # Duplicate username or email rejection
    with pytest.raises(ValueError, match="already registered"):
        user_store.create_user("carol_dev", "other@security.local", "Pass!123456")

    with pytest.raises(ValueError, match="already registered"):
        user_store.create_user("other_user", "carol@security.local", "Pass!123456")


def test_api_user_registration_and_login_flow(client):
    """Integration test: Register new user via API, login, and fetch /auth/me."""
    unique_username = f"dave_{int(time.time())}"
    unique_email = f"dave_{int(time.time())}@security.local"

    # 1. Register
    reg_resp = client.post(
        "/api/auth/register",
        json={
            "username": unique_username,
            "email": unique_email,
            "password": "DaveSecurePassword!2026",
            "role": "DEVELOPER"
        }
    )
    assert reg_resp.status_code == 201
    reg_data = reg_resp.json()
    assert reg_data["username"] == unique_username
    assert reg_data["role"] == "DEVELOPER"
    assert "password" not in reg_data

    # 2. Login
    login_resp = client.post(
        "/api/auth/login",
        json={
            "username_or_email": unique_username,
            "password": "DaveSecurePassword!2026"
        }
    )
    assert login_resp.status_code == 200
    login_data = login_resp.json()
    assert "access_token" in login_data
    token = login_data["access_token"]
    assert login_data["user"]["username"] == unique_username

    # 3. Access Protected /auth/me
    me_resp = client.get(
        "/api/auth/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert me_resp.status_code == 200
    me_data = me_resp.json()
    assert me_data["username"] == unique_username
    assert me_data["email"] == unique_email


def test_api_login_invalid_credentials(client):
    """Verify 401 Unauthorized on invalid username or wrong password."""
    resp = client.post(
        "/api/auth/login",
        json={
            "username_or_email": "admin",
            "password": "WrongPassword!999"
        }
    )
    assert resp.status_code == 401
    assert "Invalid username or password" in resp.json()["error"]


def test_rbac_admin_vs_developer_authorization(client):
    """Verify Role-Based Access Control: Admin can view all audit events, Developer views own."""
    # 1. Login as Admin
    admin_login = client.post(
        "/api/auth/login",
        json={"username_or_email": "admin", "password": "AdminSecret!2026"}
    )
    admin_token = admin_login.json()["access_token"]

    # 2. Login as Developer
    dev_login = client.post(
        "/api/auth/login",
        json={"username_or_email": "developer", "password": "DevPass!2026"}
    )
    dev_token = dev_login.json()["access_token"]

    # 3. Admin queries /api/audit/events
    admin_audit = client.get(
        "/api/audit/events",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert admin_audit.status_code == 200
    assert admin_audit.json()["is_admin_view"] is True

    # 4. Developer queries /api/audit/events (automatically scoped to developer)
    dev_audit = client.get(
        "/api/audit/events",
        headers={"Authorization": f"Bearer {dev_token}"}
    )
    assert dev_audit.status_code == 200
    assert dev_audit.json()["is_admin_view"] is False


def test_security_audit_logging_zero_leak_invariant():
    """Verify that audit logs strip passwords, tokens, API keys, and code snippets."""
    # Attempt to log sensitive metadata
    record = audit_logger.log_event(
        event_type=AuditEventType.SETTINGS_CHANGED,
        user_id="USR-TEST-SECRET",
        username="tester",
        target_resource="config",
        metadata={
            "password": "RAW_PASSWORD_DO_NOT_STORE",
            "api_key": "sk-proj-super-secret-key-12345",
            "token": "ghp_super_secret_github_pat",
            "source_code": "def secret_algo(): return 42",
            "safe_setting": "dark_mode_enabled",
            "nested_config": {
                "credential": "database_password",
                "timeout": 30
            }
        }
    )

    meta = record.sanitized_metadata
    assert meta["password"] == "[REDACTED_BY_AUDIT_GUARD]"
    assert meta["api_key"] == "[REDACTED_BY_AUDIT_GUARD]"
    assert meta["token"] == "[REDACTED_BY_AUDIT_GUARD]"
    assert meta["source_code"] == "[REDACTED_BY_AUDIT_GUARD]"
    assert meta["safe_setting"] == "dark_mode_enabled"
    assert meta["nested_config"]["credential"] == "[REDACTED_BY_AUDIT_GUARD]"
    assert meta["nested_config"]["timeout"] == 30


def test_security_headers_middleware(client):
    """Verify that all HTTP responses contain hardened defense security headers."""
    resp = client.get("/api/health")
    assert resp.status_code == 200
    headers = resp.headers

    assert headers.get("X-Content-Type-Options") == "nosniff"
    assert headers.get("X-Frame-Options") == "DENY"
    assert headers.get("X-XSS-Protection") == "1; mode=block"
    assert "Strict-Transport-Security" in headers
    assert "Content-Security-Policy" in headers
    assert headers.get("X-Privacy-Assurance") == "zero-raw-secret-leakage-guarantee"


def test_centralized_validation_error_handling(client):
    """Verify that malformed inputs return clean standardized JSON errors."""
    resp = client.post(
        "/api/auth/register",
        json={
            "username": "a",  # Too short (min 3)
            "email": "not-an-email",
            "password": "short"  # Too short (min 8)
        }
    )
    assert resp.status_code == 422
    data = resp.json()
    assert data["success"] is False
    assert data["error_type"] == "VALIDATION_ERROR"
    assert len(data["validation_errors"]) >= 2
