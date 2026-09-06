"""
Security, Cryptographic and JWT Token Utilities.
Implements NIST SP 800-63B compliant PBKDF2-HMAC password hashing and PyJWT token lifecycle management.
"""

import hashlib
import hmac
import secrets
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional
import jwt
from app.core.config import settings
from app.utils.logger import logger


class SecurityException(Exception):
    """Base exception for authentication and security authorization violations."""
    pass


class PasswordHasher:
    """
    NIST SP 800-63B compliant password hashing utility using PBKDF2-HMAC-SHA256.
    Uses 100,000 iterations and unique 32-byte cryptographically secure salts.
    """
    
    ALGORITHM: str = "sha256"
    ITERATIONS: int = 100_000
    SALT_SIZE_BYTES: int = 32

    @classmethod
    def hash_password(cls, plain_password: str) -> str:
        """
        Hash a plaintext password with a unique cryptographic salt.
        Returns format: pbkdf2_sha256$100000$<salt_hex>$<hash_hex>
        """
        if not plain_password or not isinstance(plain_password, str):
            raise ValueError("Password must be a non-empty string.")
        
        salt_bytes = secrets.token_bytes(cls.SALT_SIZE_BYTES)
        salt_hex = salt_bytes.hex()
        
        key = hashlib.pbkdf2_hmac(
            hash_name=cls.ALGORITHM,
            password=plain_password.encode("utf-8"),
            salt=salt_bytes,
            iterations=cls.ITERATIONS
        )
        hash_hex = key.hex()
        return f"pbkdf2_sha256${cls.ITERATIONS}${salt_hex}${hash_hex}"

    @classmethod
    def verify_password(cls, plain_password: str, hashed_password: str) -> bool:
        """
        Verify a plaintext password against a stored hashed password in constant time.
        """
        if not plain_password or not hashed_password:
            return False
        
        try:
            parts = hashed_password.split("$")
            if len(parts) != 4 or parts[0] != "pbkdf2_sha256":
                # Fallback for plain legacy hash or unknown format
                return False
            
            iterations = int(parts[1])
            salt_bytes = bytes.fromhex(parts[2])
            expected_hash = bytes.fromhex(parts[3])
            
            calculated_hash = hashlib.pbkdf2_hmac(
                hash_name=cls.ALGORITHM,
                password=plain_password.encode("utf-8"),
                salt=salt_bytes,
                iterations=iterations
            )
            return hmac.compare_digest(calculated_hash, expected_hash)
        except Exception as exc:
            logger.error(f"Password verification error: {exc}")
            return False


class JWTHandler:
    """
    JSON Web Token (JWT) lifecycle manager.
    Generates and decodes signed tokens with claims validation.
    """

    @classmethod
    def create_access_token(
        cls,
        subject: str,
        claims: Optional[Dict[str, Any]] = None,
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """
        Create a signed JWT access token.
        
        :param subject: Unique subject identifier (user_id)
        :param claims: Additional claims (e.g. username, role, email)
        :param expires_delta: Optional token expiration duration
        """
        now = datetime.now(timezone.utc)
        if expires_delta:
            expire = now + expires_delta
        else:
            expire = now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

        payload: Dict[str, Any] = {
            "sub": str(subject),
            "iat": int(now.timestamp()),
            "exp": int(expire.timestamp()),
            "jti": str(uuid.uuid4())
        }

        if claims:
            payload.update(claims)

        encoded_token = jwt.encode(
            payload,
            settings.JWT_SECRET_KEY,
            algorithm=settings.JWT_ALGORITHM
        )
        return encoded_token

    @classmethod
    def decode_access_token(cls, token: str) -> Dict[str, Any]:
        """
        Decode and validate a signed JWT token.
        Raises SecurityException if token is expired, tampered with, or invalid.
        """
        if not token:
            raise SecurityException("Token is missing or empty.")

        try:
            payload = jwt.decode(
                token,
                settings.JWT_SECRET_KEY,
                algorithms=[settings.JWT_ALGORITHM],
                options={"verify_exp": True, "verify_iat": True}
            )
            return payload
        except jwt.ExpiredSignatureError:
            raise SecurityException("Authentication token has expired. Please log in again.")
        except jwt.InvalidTokenError as exc:
            raise SecurityException(f"Invalid authentication token: {str(exc)}")
        except Exception as exc:
            raise SecurityException(f"Token verification error: {str(exc)}")
