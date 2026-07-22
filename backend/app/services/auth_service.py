"""
Authentication service — business logic layer.

Handles user registration, login, logout, password reset, and profile
retrieval.  Sits between the API routes and the database / security layers.
"""

from __future__ import annotations

from sqlalchemy.orm import Session

from app.core.exceptions import (
    AuthenticationError,
    UserAlreadyExistsError,
    UserNotFoundError,
)
from app.core.logger import logger
from app.core.security import (
    create_access_token,
    create_reset_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.models.database_models import BlacklistedToken, User


# ── Registration ─────────────────────────────────────────────────────────

def register_user(
    db: Session,
    email: str,
    username: str,
    full_name: str,
    password: str,
) -> User:
    """
    Create a new user account.

    Raises UserAlreadyExistsError if the email or username is taken.
    """
    # Check for duplicate email
    if db.query(User).filter(User.email == email).first():
        raise UserAlreadyExistsError("A user with this email already exists.")

    # Check for duplicate username
    if db.query(User).filter(User.username == username).first():
        raise UserAlreadyExistsError("A user with this username already exists.")

    user = User(
        email=email,
        username=username,
        full_name=full_name,
        hashed_password=hash_password(password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    logger.info("Registered new user: %s (%s)", username, email)
    return user


# ── Login ────────────────────────────────────────────────────────────────

def authenticate_user(db: Session, email: str, password: str) -> str:
    """
    Verify credentials and return a JWT access token.

    Raises AuthenticationError if the email doesn't exist, the password
    is wrong, or the account is deactivated.
    """
    user = db.query(User).filter(User.email == email).first()

    if not user:
        raise AuthenticationError("Invalid email or password.")

    if not verify_password(password, user.hashed_password):
        raise AuthenticationError("Invalid email or password.")

    if not user.is_active:
        raise AuthenticationError("This account has been deactivated.")

    token = create_access_token(user_id=user.id, email=user.email)
    logger.info("User logged in: %s", email)
    return token


# ── Logout ───────────────────────────────────────────────────────────────

def logout_user(db: Session, token_jti: str) -> None:
    """
    Blacklist a JWT token by its JTI so it cannot be reused.
    """
    blacklisted = BlacklistedToken(token_jti=token_jti)
    db.add(blacklisted)
    db.commit()
    logger.info("Token blacklisted: jti=%s", token_jti)


def is_token_blacklisted(db: Session, token_jti: str) -> bool:
    """Check whether a token JTI has been blacklisted."""
    return (
        db.query(BlacklistedToken)
        .filter(BlacklistedToken.token_jti == token_jti)
        .first()
        is not None
    )


# ── Profile ──────────────────────────────────────────────────────────────

def get_user_by_id(db: Session, user_id: str) -> User:
    """
    Fetch a user by their ID.

    Raises UserNotFoundError if not found.
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise UserNotFoundError()
    return user


# ── Forgot / Reset Password ─────────────────────────────────────────────

def request_password_reset(db: Session, email: str) -> str | None:
    """
    Generate a password reset token for the given email.

    Returns the reset token string, or None if the email isn't registered
    (we intentionally don't reveal whether the email exists for security).
    """
    user = db.query(User).filter(User.email == email).first()
    if not user:
        # Don't reveal that the email doesn't exist
        logger.info("Password reset requested for unknown email: %s", email)
        return None

    token = create_reset_token(user_id=user.id, email=user.email)
    logger.info("Password reset token generated for: %s", email)
    return token


def reset_password(db: Session, token: str, new_password: str) -> None:
    """
    Reset a user's password using a valid reset token.

    Raises AuthenticationError if the token is invalid or expired.
    """
    payload = decode_token(token)

    if not payload:
        raise AuthenticationError("Invalid or expired reset token.")

    if payload.get("type") != "reset":
        raise AuthenticationError("Invalid token type. Expected a reset token.")

    user_id = payload.get("sub")
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise UserNotFoundError("User associated with this token no longer exists.")

    user.hashed_password = hash_password(new_password)
    db.commit()

    logger.info("Password reset successfully for user: %s", user.email)


# ── Change Password ─────────────────────────────────────────────────────

def change_password(
    db: Session,
    user: User,
    current_password: str,
    new_password: str,
) -> None:
    """
    Change a logged-in user's password.

    Verifies the current password before updating.
    Raises AuthenticationError if the current password is wrong.
    """
    if not verify_password(current_password, user.hashed_password):
        raise AuthenticationError("Current password is incorrect.")

    user.hashed_password = hash_password(new_password)
    db.commit()

    logger.info("Password changed for user: %s", user.email)
