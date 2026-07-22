"""
FastAPI dependencies for authentication.

Provides the reusable `get_current_user` dependency that extracts and
validates the JWT from the Authorization header, checks the token
blacklist, and returns the authenticated User object.

Usage in any route:

    from app.api.deps import get_current_user
    from app.models.database_models import User

    @router.get("/protected")
    def protected_route(current_user: User = Depends(get_current_user)):
        ...
"""

from __future__ import annotations

from fastapi import Depends, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.exceptions import AuthenticationError
from app.core.security import decode_token
from app.models.database_models import User
from app.services.auth_service import is_token_blacklisted

# Use HTTPBearer scheme — expects "Authorization: Bearer <token>"
_bearer_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    """
    Validate the JWT access token and return the authenticated user.

    Raises AuthenticationError (401) if:
      - No token is provided
      - The token is invalid / expired
      - The token has been blacklisted (user logged out)
      - The user no longer exists or is deactivated
    """
    if credentials is None:
        raise AuthenticationError("Not authenticated. Please provide a Bearer token.")

    token = credentials.credentials
    payload = decode_token(token)

    if payload is None:
        raise AuthenticationError("Invalid or expired access token.")

    # Ensure this is an access token, not a reset token
    if payload.get("type") != "access":
        raise AuthenticationError("Invalid token type.")

    # Check blacklist (logout support)
    jti = payload.get("jti")
    if jti and is_token_blacklisted(db, jti):
        raise AuthenticationError("This token has been revoked. Please log in again.")

    # Fetch the user
    user_id = payload.get("sub")
    user = db.query(User).filter(User.id == user_id).first()

    if user is None:
        raise AuthenticationError("User not found.")

    if not user.is_active:
        raise AuthenticationError("This account has been deactivated.")

    return user
