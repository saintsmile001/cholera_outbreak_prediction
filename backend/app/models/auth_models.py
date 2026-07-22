"""
Pydantic schemas for authentication requests and responses.

Every auth-related API request/response body is validated against
these models.
"""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


# ── Requests ─────────────────────────────────────────────────────────────

class RegisterRequest(BaseModel):
    """Schema for user registration."""
    email: str = Field(
        ...,
        min_length=5,
        max_length=255,
        description="User's email address.",
        examples=["user@example.com"],
    )
    username: str = Field(
        ...,
        min_length=3,
        max_length=50,
        pattern=r"^[a-zA-Z0-9_]+$",
        description="Username (alphanumeric + underscores only).",
        examples=["john_doe"],
    )
    full_name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="User's full name.",
        examples=["John Doe"],
    )
    password: str = Field(
        ...,
        min_length=8,
        max_length=128,
        description="Password (minimum 8 characters).",
        examples=["SecureP@ss123"],
    )


class LoginRequest(BaseModel):
    """Schema for user login."""
    email: str = Field(
        ...,
        min_length=5,
        max_length=255,
        description="Registered email address.",
        examples=["user@example.com"],
    )
    password: str = Field(
        ...,
        min_length=1,
        description="Account password.",
        examples=["SecureP@ss123"],
    )


class ForgotPasswordRequest(BaseModel):
    """Schema for requesting a password reset token."""
    email: str = Field(
        ...,
        min_length=5,
        max_length=255,
        description="Email address of the account to reset.",
        examples=["user@example.com"],
    )


class ResetPasswordRequest(BaseModel):
    """Schema for resetting a password with a reset token."""
    token: str = Field(
        ...,
        min_length=1,
        description="The password reset token received via /forgot-password.",
    )
    new_password: str = Field(
        ...,
        min_length=8,
        max_length=128,
        description="New password (minimum 8 characters).",
        examples=["NewSecureP@ss456"],
    )


class ChangePasswordRequest(BaseModel):
    """Schema for changing password while logged in."""
    current_password: str = Field(
        ...,
        min_length=1,
        description="Current account password.",
    )
    new_password: str = Field(
        ...,
        min_length=8,
        max_length=128,
        description="New password (minimum 8 characters).",
        examples=["NewSecureP@ss456"],
    )


# ── Responses ────────────────────────────────────────────────────────────

class TokenResponse(BaseModel):
    """Response containing a JWT access token."""
    access_token: str = Field(..., description="JWT access token.")
    token_type: str = Field(default="bearer", description="Token type.")


class UserResponse(BaseModel):
    """Public user profile response."""
    id: str = Field(..., description="User ID.")
    email: str = Field(..., description="Email address.")
    username: str = Field(..., description="Username.")
    full_name: str = Field(..., description="Full name.")
    is_active: bool = Field(..., description="Whether the account is active.")
    created_at: datetime = Field(..., description="Account creation timestamp.")

    model_config = {"from_attributes": True}


class AuthMessageResponse(BaseModel):
    """Generic auth message response."""
    message: str = Field(..., description="Status message.")


class ForgotPasswordResponse(BaseModel):
    """
    Response for forgot-password requests.

    In production the token would be sent via email.
    For the hackathon it is returned directly so you can test the flow.
    """
    message: str = Field(..., description="Status message.")
    reset_token: str | None = Field(
        None,
        description="Reset token (returned directly for hackathon/demo purposes).",
    )
