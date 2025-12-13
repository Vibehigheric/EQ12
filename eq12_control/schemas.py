#!/usr/bin/env python3
"""
EQ12 Control Plane Pydantic Schemas
===================================

SPDX-License-Identifier: MIT
SPDX-FileCopyrightText: 2025 EQ12 Project Contributors

Request/response schemas for API validation.
"""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field, validator


# Base schemas
class BaseResponse(BaseModel):
    """Base response with common fields."""

    request_id: str = Field(..., description="Unique request identifier")
    timestamp: datetime = Field(default_factory=datetime.utcnow)


# Authentication schemas
class MagicLinkRequest(BaseModel):
    """Request magic link for passwordless auth."""

    email: str = Field(..., description="User email address")


class MagicLinkResponse(BaseResponse):
    """Magic link generation response."""

    message: str = "Magic link sent"
    expires_in: int = 900  # 15 minutes


class TokenResponse(BaseResponse):
    """JWT token response."""

    access_token: str
    token_type: str = "bearer"
    expires_in: int


# Tenant schemas
class TenantCreate(BaseModel):
    """Create new tenant."""

    name: str = Field(..., min_length=1, max_length=100)
    slug: str = Field(..., min_length=1, max_length=50)

    @validator("slug")
    def slug_must_be_valid(cls, v):
        import re

        if not re.match(r"^[a-z0-9-]+$", v):
            raise ValueError("Slug must contain only lowercase letters, numbers, and hyphens")
        return v


class Tenant(BaseModel):
    """Tenant response."""

    id: int
    name: str
    slug: str
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


class TenantResponse(BaseResponse):
    """Tenant creation/fetch response."""

    tenant: Tenant


# User schemas
class UserInvite(BaseModel):
    """Invite user to tenant."""

    email: str = Field(..., description="User email")
    role: str = Field(..., description="User role")

    @validator("role")
    def role_must_be_valid(cls, v):
        valid_roles = ["owner", "admin", "analyst", "billing", "readonly"]
        if v not in valid_roles:
            raise ValueError(f"Role must be one of: {valid_roles}")
        return v


class User(BaseModel):
    """User response."""

    id: int
    email: str
    name: str
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


class Membership(BaseModel):
    """User membership in tenant."""

    user: User
    role: str
    created_at: datetime

    class Config:
        from_attributes = True


class UsersResponse(BaseResponse):
    """Tenant users list response."""

    users: list[Membership]


# API Key schemas
class APIKeyCreate(BaseModel):
    """Create new API key."""

    name: str = Field(..., min_length=1, max_length=100)
    scopes: str = Field(default="*", description="Comma-separated scopes")


class APIKey(BaseModel):
    """API key response (without secret)."""

    id: int
    name: str
    scopes: str
    active: bool
    created_at: datetime
    last_used_at: datetime | None

    class Config:
        from_attributes = True


class APIKeyCreateResponse(BaseResponse):
    """API key creation response."""

    api_key: APIKey
    key_secret: str = Field(..., description="Store securely - only shown once")


class APIKeyRotateResponse(BaseResponse):
    """API key rotation response."""

    new_key_secret: str = Field(..., description="New key - store securely")


# Plan schemas
class Plan(BaseModel):
    """Subscription plan."""

    id: int
    code: str
    name: str
    limits_json: dict[str, Any]
    price_month: float | None
    price_year: float | None
    active: bool

    class Config:
        from_attributes = True


class PlansResponse(BaseResponse):
    """Plans list response."""

    plans: list[Plan]


# Billing schemas
class CheckoutRequest(BaseModel):
    """Create checkout session."""

    plan_code: str = Field(..., description="Plan to subscribe to")
    billing_cycle: str = Field(..., description="monthly or yearly")

    @validator("billing_cycle")
    def billing_cycle_must_be_valid(cls, v):
        if v not in ["monthly", "yearly"]:
            raise ValueError("Billing cycle must be monthly or yearly")
        return v


class CheckoutResponse(BaseResponse):
    """Checkout session response."""

    checkout_url: str
    session_id: str


class WebhookEvent(BaseModel):
    """Webhook event payload."""

    provider: str
    event_type: str
    data: dict[str, Any]


# Usage schemas
class UsageEvent(BaseModel):
    """Usage event for metering."""

    service: str = Field(..., description="Service name (api, ai, sim)")
    model: str | None = Field(None, description="Model used")
    tokens_in: int = Field(default=0, ge=0)
    tokens_out: int = Field(default=0, ge=0)
    cost_usd: float = Field(default=0.0, ge=0.0)
    meta: dict[str, Any] | None = Field(None, description="Additional metadata")


class UsageIngestRequest(BaseModel):
    """Batch usage ingestion."""

    events: list[UsageEvent] = Field(..., max_items=100)


class UsageIngestResponse(BaseResponse):
    """Usage ingestion response."""

    events_processed: int
    total_cost: float


class UsageSummary(BaseModel):
    """Usage summary statistics."""

    period_start: datetime
    period_end: datetime
    total_requests: int
    total_tokens_in: int
    total_tokens_out: int
    total_cost_usd: float
    by_service: dict[str, dict[str, Any]]


class UsageSummaryResponse(BaseResponse):
    """Usage summary response."""

    summary: UsageSummary


# Limits schemas
class Limits(BaseModel):
    """Effective limits for tenant."""

    requests_per_minute: int
    tokens_per_minute: int
    tokens_per_day: int
    features: list[str]
    cost_limit_usd: float | None


class LimitsResponse(BaseResponse):
    """Limits response."""

    limits: Limits
    current_usage: dict[str, int]


# License schemas
class LicenseConsumeRequest(BaseModel):
    """Consume license request."""

    service: str
    tokens: int = Field(default=1, ge=1)
    cost_usd: float | None = Field(None, ge=0.0)


class LicenseConsumeResponse(BaseResponse):
    """License consume response."""

    allowed: bool
    remaining_tokens: int | None
    remaining_cost: float | None
    reset_at: datetime | None


# Audit schemas
class AuditLog(BaseModel):
    """Audit log entry."""

    id: int
    action: str
    target: str | None
    ts_utc: datetime
    ip_address: str | None
    meta_json: dict[str, Any] | None
    actor_user_email: str | None

    class Config:
        from_attributes = True


class AuditLogsResponse(BaseResponse):
    """Audit logs list response."""

    logs: list[AuditLog]
    total: int
    page: int
    page_size: int


# Health schema
class HealthResponse(BaseModel):
    """Health check response."""

    status: str = "ok"
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    version: str = "1.0.0"
    database: bool
    uptime_seconds: float


# Additional missing schemas for routers


class LoginRequest(BaseModel):
    """Login request with token."""

    token: str


class LoginResponse(BaseModel):
    """Login response with tokens."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class TokenRefreshRequest(BaseModel):
    """Token refresh request."""

    refresh_token: str


class TokenRefreshResponse(BaseModel):
    """Token refresh response."""

    access_token: str
    token_type: str = "bearer"
    expires_in: int


class TenantCreateRequest(BaseModel):
    """Create tenant request."""

    name: str
    display_name: str
    settings: dict[str, Any] | None = None


class TenantCreateResponse(BaseModel):
    """Create tenant response."""

    id: int
    name: str
    display_name: str
    created_at: datetime


class TenantUpdateRequest(BaseModel):
    """Update tenant request."""

    display_name: str | None = None
    settings: dict[str, Any] | None = None


class TenantResponse(BaseModel):
    """Tenant details response."""

    id: int
    name: str
    display_name: str
    created_at: datetime
    is_active: bool
    user_count: int | None = None


class UserInviteRequest(BaseModel):
    """User invitation request."""

    email: str
    role: str = "member"
    full_name: str | None = None


class UserInviteResponse(BaseModel):
    """User invitation response."""

    message: str
    email: str
    role: str


class UserResponse(BaseModel):
    """User details response."""

    id: int
    email: str
    full_name: str
    is_active: bool
    is_admin: bool
    created_at: datetime
    last_login: datetime | None = None


class UserUpdateRequest(BaseModel):
    """User update request."""

    full_name: str | None = None


class APIKeyCreateRequest(BaseModel):
    """API key creation request."""

    name: str
    scopes: list[str] | None = None


class APIKeyCreateResponse(BaseModel):
    """API key creation response."""

    id: int
    name: str
    key: str  # Only returned once
    scopes: list[str]
    created_at: datetime


class APIKeyResponse(BaseModel):
    """API key details response."""

    id: int
    name: str
    scopes: list[str]
    created_at: datetime
    last_used: datetime | None = None
    is_active: bool
