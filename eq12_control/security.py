#!/usr/bin/env python3
"""
EQ12 Control Plane Security
==========================

SPDX-License-Identifier: MIT
SPDX-FileCopyrightText: 2025 EQ12 Project Contributors

JWT authentication, key rotation, and security utilities.
"""

import hashlib
import hmac
import secrets
from datetime import UTC, datetime, timedelta
from typing import Any

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from passlib.context import CryptContext

from .config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()


class SecurityManager:
    """Handles JWT tokens, API keys, and authentication."""

    def __init__(self):
        self.algorithm = settings.jwt_algorithm
        self.secret_key = settings.jwt_secret_key

    def create_jwt_token(self, data: dict[str, Any], expires_delta: timedelta | None = None) -> str:
        """Create a JWT token with expiration."""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.now(UTC) + expires_delta
        else:
            expire = datetime.now(UTC) + timedelta(minutes=settings.jwt_expire_minutes)

        to_encode.update({"exp": expire, "iat": datetime.now(UTC)})
        return jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)

    def verify_jwt_token(self, token: str) -> dict[str, Any] | None:
        """Verify and decode a JWT token."""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except JWTError:
            return None

    def hash_api_key(self, api_key: str) -> str:
        """Hash API key for secure storage."""
        return hashlib.sha256(api_key.encode()).hexdigest()

    def generate_api_key(self) -> str:
        """Generate a new API key."""
        return f"eq12_{secrets.token_urlsafe(32)}"

    def verify_api_key_hash(self, api_key: str, hashed: str) -> bool:
        """Verify API key against stored hash."""
        return self.hash_api_key(api_key) == hashed

    def verify_webhook_signature(self, payload: bytes, signature: str, secret: str) -> bool:
        """Verify HMAC webhook signature."""
        expected_signature = hmac.new(secret.encode(), payload, hashlib.sha256).hexdigest()
        return hmac.compare_digest(signature, f"sha256={expected_signature}")

    def generate_csrf_token(self) -> str:
        """Generate CSRF token for forms."""
        return secrets.token_urlsafe(32)

    def generate_magic_link_token(self, email: str, expires_minutes: int = 15) -> str:
        """Generate magic link token for passwordless auth."""
        data = {
            "email": email,
            "type": "magic_link",
            "exp": datetime.now(UTC) + timedelta(minutes=expires_minutes),
        }
        return self.create_jwt_token(data)


security_manager = SecurityManager()


async def get_current_user_from_jwt(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Extract current user from JWT token."""
    token = credentials.credentials
    payload = security_manager.verify_jwt_token(token)

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return payload


async def verify_api_key_dependency(request: Request):
    """Verify API key from header."""
    api_key = request.headers.get("X-API-Key")
    if not api_key:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="API key required")

    # This would normally query the database to verify the key
    # For now, return a placeholder tenant_id
    return {"tenant_id": "default", "api_key": api_key}


def hash_password(password: str) -> str:
    """Hash a password."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)
