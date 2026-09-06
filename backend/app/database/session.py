"""
Database Engine, Session Management, and Connection Health Check.
"""

import time
from typing import Generator, Dict, Any
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from app.core.config import settings
from app.core.constants import ComponentStatus
from app.utils.logger import logger

# Create SQLAlchemy Engine
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
    connect_args={"connect_timeout": 3} if "postgresql" in settings.DATABASE_URL else {}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    """
    FastAPI Dependency to yield a database session per request.
    Closes the session automatically upon completion.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def check_database_connection() -> Dict[str, Any]:
    """
    Test connectivity to the configured database.
    Returns status dictionary without throwing uncaught exceptions.
    """
    start_time = time.perf_counter()
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        latency_ms = round((time.perf_counter() - start_time) * 1000, 2)
        return {
            "status": ComponentStatus.CONNECTED.value,
            "database_type": "PostgreSQL",
            "host": settings.POSTGRES_HOST,
            "database_name": settings.POSTGRES_DB,
            "latency_ms": latency_ms,
            "message": "Database connection healthy"
        }
    except Exception as exc:
        logger.warning(f"Database connection check failed: {exc}")
        return {
            "status": ComponentStatus.DISCONNECTED.value,
            "database_type": "PostgreSQL",
            "host": settings.POSTGRES_HOST,
            "database_name": settings.POSTGRES_DB,
            "latency_ms": None,
            "message": f"Database unreachable: {str(exc).splitlines()[0] if str(exc) else 'Connection error'}"
        }
