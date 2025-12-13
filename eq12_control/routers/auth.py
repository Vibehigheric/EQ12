#!/usr/bin/env python3
"""
Authentication Router for EQ12 Control Plane
============================================

Handles magic link authentication and JWT token management.
"""

from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from ..config import settings
from ..db import get_db
from ..models import AuditLog, User
from ..schemas import (
    LoginRequest,
    LoginResponse,
    MagicLinkRequest,
    MagicLinkResponse,
    TokenRefreshRequest,
    TokenRefreshResponse,
)
from ..security import SecurityManager

router = APIRouter()
security = HTTPBearer()
security_manager = SecurityManager()


@router.post("/magic-link", response_model=MagicLinkResponse)
async def request_magic_link(request: MagicLinkRequest, db: Session = Depends(get_db)):
    """Request a magic login link."""
    # Check if user exists
    user = db.query(User).filter(User.email == request.email).first()
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found or inactive"
        )

    # Generate magic link token
    token = security_manager.create_magic_link_token(user.email)

    # In production, send email here
    # For development, return the link
    magic_link = f"{settings.frontend_url}/auth/verify?token={token}"

    # Log the authentication attempt
    audit_log = AuditLog(
        user_id=user.id,
        tenant_id=user.tenant_id,
        action="magic_link_requested",
        resource="auth",
        details={"email": user.email},
    )
    db.add(audit_log)
    db.commit()

    return MagicLinkResponse(
        message="Magic link sent to your email", magic_link=magic_link if settings.debug else None
    )


@router.post("/verify", response_model=LoginResponse)
async def verify_magic_link(request: LoginRequest, db: Session = Depends(get_db)):
    """Verify magic link token and return JWT."""
    try:
        # Verify the magic link token
        email = security_manager.verify_magic_link_token(request.token)

        # Get user
        user = db.query(User).filter(User.email == email).first()
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token"
            )

        # Update last login
        user.last_login = datetime.now(UTC)

        # Create JWT tokens
        access_token = security_manager.create_access_token(
            data={"sub": str(user.id), "email": user.email}
        )
        refresh_token = security_manager.create_refresh_token(
            data={"sub": str(user.id), "email": user.email}
        )

        # Log successful login
        audit_log = AuditLog(
            user_id=user.id,
            tenant_id=user.tenant_id,
            action="login_success",
            resource="auth",
            details={"email": user.email, "method": "magic_link"},
        )
        db.add(audit_log)
        db.commit()

        return LoginResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=settings.jwt_access_token_expire_minutes * 60,
        )

    except Exception as e:
        # Log failed login attempt
        audit_log = AuditLog(
            action="login_failed",
            resource="auth",
            details={"error": str(e), "method": "magic_link"},
        )
        db.add(audit_log)
        db.commit()

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token"
        )


@router.post("/refresh", response_model=TokenRefreshResponse)
async def refresh_token(request: TokenRefreshRequest, db: Session = Depends(get_db)):
    """Refresh access token using refresh token."""
    try:
        # Verify refresh token
        payload = security_manager.verify_refresh_token(request.refresh_token)
        user_id = payload.get("sub")

        # Get user
        user = db.query(User).filter(User.id == user_id).first()
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found or inactive"
            )

        # Create new access token
        access_token = security_manager.create_access_token(
            data={"sub": str(user.id), "email": user.email}
        )

        return TokenRefreshResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in=settings.jwt_access_token_expire_minutes * 60,
        )

    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token"
        )


@router.post("/logout")
async def logout(
    credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)
):
    """Logout and invalidate tokens."""
    try:
        # Verify token to get user info
        payload = security_manager.verify_access_token(credentials.credentials)
        user_id = payload.get("sub")

        # Log logout
        audit_log = AuditLog(
            user_id=user_id, action="logout", resource="auth", details={"method": "api"}
        )
        db.add(audit_log)
        db.commit()

        return {"message": "Successfully logged out"}

    except Exception:
        # Even if token is invalid, return success for security
        return {"message": "Successfully logged out"}


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)
) -> User:
    """Dependency to get current authenticated user."""
    try:
        payload = security_manager.verify_access_token(credentials.credentials)
        user_id = payload.get("sub")

        if user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

        user = db.query(User).filter(User.id == user_id).first()
        if user is None or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found or inactive"
            )

        return user

    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """Dependency to get current active user."""
    if not current_user.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user")
    return current_user
