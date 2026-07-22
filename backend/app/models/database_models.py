"""
SQLAlchemy ORM models for the database.

Defines the User and BlacklistedToken tables.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, Column, DateTime, String, Text
from sqlalchemy.sql import func

from app.core.database import Base


def _generate_uuid() -> str:
    """Generate a new UUID4 string."""
    return str(uuid.uuid4())


class User(Base):
    """Application user account."""

    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=_generate_uuid)
    email = Column(String(255), unique=True, nullable=False, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    full_name = Column(String(100), nullable=False)
    hashed_password = Column(Text, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    def __repr__(self) -> str:
        return f"<User id={self.id} email={self.email}>"


class BlacklistedToken(Base):
    """
    Stores blacklisted JWT token IDs (JTIs) for logout support.

    When a user logs out, their token's unique JTI is added here.
    The auth dependency checks this table before granting access.
    """

    __tablename__ = "blacklisted_tokens"

    id = Column(String(36), primary_key=True, default=_generate_uuid)
    token_jti = Column(String(36), unique=True, nullable=False, index=True)
    blacklisted_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    def __repr__(self) -> str:
        return f"<BlacklistedToken jti={self.token_jti}>"
