"""
SQLAlchemy Declarative Base for ORM Models.
"""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy ORM models in the modular monolith."""
    pass
