"""
Authentication routes.

Provides endpoints for user registration, login, logout, profile,
forgot/reset password, and change password.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.core.security import decode_token
from app.models.auth_models import (
    AuthMessageResponse,
    ChangePasswordRequest,
    ForgotPasswordRequest,
    ForgotPasswordResponse,
    LoginRequest,
    RegisterRequest,
    ResetPasswordRequest,
    TokenResponse,
    UserResponse,
)
from app.models.database_models import User
from app.services.auth_service import (
    authenticate_user,
    change_password,
    logout_user,
    register_user,
    request_password_reset,
    reset_password,
)

router = APIRouter(prefix="/api/v1/auth", tags=["authentication"])


# ── Register ─────────────────────────────────────────────────────────────

@router.post(
    "/register",
    response_model=UserResponse,
    status_code=201,
    summary="Create a new account",
    description="Register a new user with email, username, full name, and password.",
)
def register(request: RegisterRequest, db: Session = Depends(get_db)):
    """Create a new user account and return the user profile."""
    user = register_user(
        db=db,
        email=request.email,
        username=request.username,
        full_name=request.full_name,
        password=request.password,
    )
    return user


# ── Login ────────────────────────────────────────────────────────────────

@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Login",
    description="Authenticate with email and password. Returns a JWT access token.",
)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    """Verify credentials and return an access token."""
    token = authenticate_user(db=db, email=request.email, password=request.password)
    return TokenResponse(access_token=token)


# ── Logout ───────────────────────────────────────────────────────────────

@router.post(
    "/logout",
    response_model=AuthMessageResponse,
    summary="Logout",
    description="Invalidate the current access token. Requires authentication.",
)
def logout(
    current_user: User = Depends(get_current_user),
    credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer()),
    db: Session = Depends(get_db),
):
    """Blacklist the current token so it can no longer be used."""
    payload = decode_token(credentials.credentials)
    if payload and payload.get("jti"):
        logout_user(db=db, token_jti=payload["jti"])
    return AuthMessageResponse(message="Successfully logged out.")


# ── Me (Profile) ─────────────────────────────────────────────────────────

@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get current user profile",
    description="Returns the profile of the currently authenticated user.",
)
def me(current_user: User = Depends(get_current_user)):
    """Return the authenticated user's profile."""
    return current_user


# ── Forgot Password ─────────────────────────────────────────────────────

@router.post(
    "/forgot-password",
    response_model=ForgotPasswordResponse,
    summary="Request password reset",
    description=(
        "Submit your email to receive a password reset token. "
        "For the hackathon, the token is returned in the response. "
        "In production it would be sent via email."
    ),
)
def forgot_password(request: ForgotPasswordRequest, db: Session = Depends(get_db)):
    """Generate a password reset token for the given email."""
    token = request_password_reset(db=db, email=request.email)

    if token is None:
        # Don't reveal whether the email exists — always return success
        return ForgotPasswordResponse(
            message="If an account with that email exists, a reset token has been generated.",
            reset_token=None,
        )

    return ForgotPasswordResponse(
        message="Password reset token generated. Use it with /reset-password.",
        reset_token=token,
    )


# ── Reset Password ──────────────────────────────────────────────────────

@router.post(
    "/reset-password",
    response_model=AuthMessageResponse,
    summary="Reset password",
    description="Reset your password using the token from /forgot-password.",
)
def do_reset_password(request: ResetPasswordRequest, db: Session = Depends(get_db)):
    """Reset a user's password using a valid reset token."""
    reset_password(db=db, token=request.token, new_password=request.new_password)
    return AuthMessageResponse(message="Password has been reset successfully. You can now log in.")


# ── Change Password ─────────────────────────────────────────────────────

@router.post(
    "/change-password",
    response_model=AuthMessageResponse,
    summary="Change password",
    description="Change your password while logged in. Requires authentication.",
)
def do_change_password(
    request: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Change the authenticated user's password."""
    change_password(
        db=db,
        user=current_user,
        current_password=request.current_password,
        new_password=request.new_password,
    )
    return AuthMessageResponse(message="Password changed successfully.")
