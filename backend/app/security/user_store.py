"""
In-Memory Thread-Safe User Repository.
Provides storage and retrieval for platform user accounts with pre-seeded administrative and developer profiles.
"""

import threading
import uuid
from datetime import datetime, timezone
from typing import Dict, List, Optional
from app.core.security import PasswordHasher
from app.schemas.auth import UserRecord, UserRole
from app.utils.logger import logger


class InMemoryUserStore:
    """
    Thread-safe repository for user credentials and authorization roles.
    """

    def __init__(self, preseed: bool = True):
        self._lock = threading.Lock()
        self._users_by_id: Dict[str, UserRecord] = {}
        self._users_by_username: Dict[str, str] = {}  # username.lower() -> user_id
        self._users_by_email: Dict[str, str] = {}     # email.lower() -> user_id

        if preseed:
            self._preseed_default_users()

    def _preseed_default_users(self) -> None:
        """Seed initial administrator and developer accounts."""
        try:
            # 1. Administrator Account
            admin_id = "USR-ADMIN-0000-000000000001"
            admin_hash = PasswordHasher.hash_password("AdminSecret!2026")
            admin_user = UserRecord(
                id=admin_id,
                username="admin",
                email="admin@security.local",
                hashed_password=admin_hash,
                role=UserRole.ADMIN,
                is_active=True,
                created_at=datetime.now(timezone.utc)
            )
            self._users_by_id[admin_id] = admin_user
            self._users_by_username[admin_user.username.lower()] = admin_id
            self._users_by_email[admin_user.email.lower()] = admin_id

            # 2. Developer Account
            dev_id = "USR-DEV-0000-000000000002"
            dev_hash = PasswordHasher.hash_password("DevPass!2026")
            dev_user = UserRecord(
                id=dev_id,
                username="developer",
                email="dev@security.local",
                hashed_password=dev_hash,
                role=UserRole.DEVELOPER,
                is_active=True,
                created_at=datetime.now(timezone.utc)
            )
            self._users_by_id[dev_id] = dev_user
            self._users_by_username[dev_user.username.lower()] = dev_id
            self._users_by_email[dev_user.email.lower()] = dev_id

            logger.info("InMemoryUserStore: Pre-seeded default admin and developer accounts.")
        except Exception as exc:
            logger.error(f"Failed to preseed default users: {exc}")

    def get_by_id(self, user_id: str) -> Optional[UserRecord]:
        """Fetch user by unique UUID."""
        with self._lock:
            return self._users_by_id.get(user_id)

    def get_by_username(self, username: str) -> Optional[UserRecord]:
        """Fetch user by case-insensitive username."""
        with self._lock:
            user_id = self._users_by_username.get(username.lower().strip())
            return self._users_by_id.get(user_id) if user_id else None

    def get_by_email(self, email: str) -> Optional[UserRecord]:
        """Fetch user by case-insensitive email address."""
        with self._lock:
            user_id = self._users_by_email.get(email.lower().strip())
            return self._users_by_id.get(user_id) if user_id else None

    def get_by_username_or_email(self, identifier: str) -> Optional[UserRecord]:
        """Fetch user by matching either username or email."""
        clean = identifier.lower().strip()
        with self._lock:
            user_id = self._users_by_username.get(clean) or self._users_by_email.get(clean)
            return self._users_by_id.get(user_id) if user_id else None

    def create_user(
        self,
        username: str,
        email: str,
        plain_password: str,
        role: UserRole = UserRole.DEVELOPER
    ) -> UserRecord:
        """
        Create and persist a new user record.
        Raises ValueError if username or email is already registered.
        """
        u_clean = username.strip()
        e_clean = email.lower().strip()

        with self._lock:
            if u_clean.lower() in self._users_by_username:
                raise ValueError(f"Username '{u_clean}' is already registered.")
            if e_clean in self._users_by_email:
                raise ValueError(f"Email '{e_clean}' is already registered.")

            user_id = f"USR-{uuid.uuid4().hex[:12].upper()}"
            hashed = PasswordHasher.hash_password(plain_password)
            record = UserRecord(
                id=user_id,
                username=u_clean,
                email=e_clean,
                hashed_password=hashed,
                role=role,
                is_active=True,
                created_at=datetime.now(timezone.utc)
            )

            self._users_by_id[user_id] = record
            self._users_by_username[u_clean.lower()] = user_id
            self._users_by_email[e_clean] = user_id

            logger.info(f"InMemoryUserStore: Registered user '{u_clean}' (role={role.value}, id={user_id})")
            return record

    def update_last_login(self, user_id: str) -> None:
        """Update last login timestamp for a user."""
        with self._lock:
            user = self._users_by_id.get(user_id)
            if user:
                user.last_login_at = datetime.now(timezone.utc)

    def list_users(self) -> List[UserRecord]:
        """Return list of all registered users."""
        with self._lock:
            return list(self._users_by_id.values())

    def count(self) -> int:
        """Return total count of registered users."""
        with self._lock:
            return len(self._users_by_id)


# Global singleton instance
user_store = InMemoryUserStore(preseed=True)
