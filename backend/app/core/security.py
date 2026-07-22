"""
Security utilities — password hashing and JWT token management.

Uses passlib with bcrypt for password hashing and python-jose for
JWT creation and verification.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone

import bcrypt
from jose import JWTError, jwt

from app.core.config import settings
from app.core.logger import logger

# ── Password hashing ────────────────────────────────────────────────────

def hash_password(plain_password: str) -> str:
    """Hash a plain-text password using bcrypt (truncated to 72 bytes max as per bcrypt spec)."""
    pwd_bytes = plain_password.encode("utf-8")[:72]
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(pwd_bytes, salt).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain-text password against its bcrypt hash."""
    pwd_bytes = plain_password.encode("utf-8")[:72]
    hash_bytes = hashed_password.encode("utf-8")
    return bcrypt.checkpw(pwd_bytes, hash_bytes)


# ── JWT Tokens ───────────────────────────────────────────────────────────

def create_access_token(user_id: str, email: str) -> str:
    """
    Create a JWT access token for an authenticated user.

    The token contains the user's ID as `sub`, their email, a unique
    token ID (`jti`) for blacklist support, and an expiry time.
    """
    jti = str(uuid.uuid4())
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)

    payload = {
        "sub": user_id,
        "email": email,
        "jti": jti,
        "exp": expire,
        "type": "access",
    }
    token = jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    logger.debug("Created access token for user=%s, jti=%s", user_id, jti)
    return token


def create_reset_token(user_id: str, email: str) -> str:
    """
    Create a short-lived JWT token for password reset.

    Distinct from access tokens via the `type` claim.
    """
    jti = str(uuid.uuid4())
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.JWT_RESET_TOKEN_EXPIRE_MINUTES)

    payload = {
        "sub": user_id,
        "email": email,
        "jti": jti,
        "exp": expire,
        "type": "reset",
    }
    token = jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    logger.debug("Created reset token for user=%s", user_id)
    return token


def decode_token(token: str) -> dict | None:
    """
    Decode and validate a JWT token.

    Returns the payload dict on success, or None if the token is
    invalid, expired, or malformed.
    """
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
        return payload
    except JWTError as exc:
        logger.warning("JWT decode failed: %s", exc)
        return None
