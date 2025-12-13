#!/usr/bin/env python3
"""
EQ12 Control Plane Database Models
=================================

SPDX-License-Identifier: MIT
SPDX-FileCopyrightText: 2025 EQ12 Project Contributors

SQLAlchemy models for multi-tenant SaaS platform.
"""

from datetime import UTC, datetime

from sqlalchemy import (
    JSON,
    BigInteger,
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
)
from sqlalchemy.orm import relationship

from .db import Base


class Tenant(Base):
    """Multi-tenant organization/workspace."""

    __tablename__ = "tenants"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True)
    display_name = Column(String(200), nullable=False)
    is_active = Column(Boolean, default=True, index=True)
    settings = Column(JSON, default=dict)
    created_at = Column(DateTime, default=lambda: datetime.now(UTC))

    # Relationships
    users = relationship("User", back_populates="tenant")
    memberships = relationship("Membership", back_populates="tenant")
    subscriptions = relationship("Subscription", back_populates="tenant")
    api_keys = relationship("APIKey", back_populates="tenant")
    usage_events = relationship("UsageEvent", back_populates="tenant")
    audit_logs = relationship("AuditLog", back_populates="tenant")
    invoices = relationship("Invoice", back_populates="tenant")


class User(Base):
    """User accounts."""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    full_name = Column(String(100), nullable=False, default="")
    is_active = Column(Boolean, default=True, index=True)
    is_admin = Column(Boolean, default=False, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(UTC))
    last_login = Column(DateTime, nullable=True)

    # Relationships
    tenant = relationship("Tenant", back_populates="users")
    memberships = relationship("Membership", back_populates="user")
    audit_logs = relationship("AuditLog", back_populates="actor_user")
    api_keys = relationship("APIKey", back_populates="user")


class Membership(Base):
    """User membership in tenants with roles."""

    __tablename__ = "memberships"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    role = Column(String(20), nullable=False)  # owner, admin, analyst
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(UTC))

    # Relationships
    tenant = relationship("Tenant", back_populates="memberships")
    user = relationship("User", back_populates="memberships")

    # Composite index
    __table_args__ = (Index("idx_tenant_user", "tenant_id", "user_id"),)


class Plan(Base):
    """Subscription plans with limits and pricing."""

    __tablename__ = "plans"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(100), nullable=False)
    limits_json = Column(JSON, nullable=False)  # RPM, TPM, TPD, features
    price_month = Column(Float, nullable=True)
    price_year = Column(Float, nullable=True)
    active = Column(Boolean, default=True, index=True)
    created_at = Column(DateTime, default=lambda: datetime.now(UTC))

    # Relationships
    subscriptions = relationship("Subscription", back_populates="plan")


class Subscription(Base):
    """Tenant subscriptions to plans."""

    __tablename__ = "subscriptions"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False)
    plan_id = Column(Integer, ForeignKey("plans.id"), nullable=False)
    provider = Column(String(20), nullable=False)  # paypal, cashapp, venmo
    external_id = Column(String(100), nullable=True, index=True)
    status = Column(String(20), nullable=False, index=True)  # active, cancelled, past_due
    renews_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(UTC))

    # Relationships
    tenant = relationship("Tenant", back_populates="subscriptions")
    plan = relationship("Plan", back_populates="subscriptions")

    # Index for provider lookups
    __table_args__ = (Index("idx_subscription_provider_external", "provider", "external_id"),)


class APIKey(Base):
    """API keys for programmatic access."""

    __tablename__ = "api_keys"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False)
    name = Column(String(100), nullable=False)
    key_hash = Column(String(64), nullable=False, index=True)
    scopes = Column(JSON, default=list)  # List of permissions
    is_active = Column(Boolean, default=True, index=True)
    created_at = Column(DateTime, default=lambda: datetime.now(UTC))
    last_used = Column(DateTime, nullable=True)

    # Relationships
    user = relationship("User", back_populates="api_keys")
    tenant = relationship("Tenant", back_populates="api_keys")


class UsageEvent(Base):
    """Usage tracking for metering and billing."""

    __tablename__ = "usage_events"

    id = Column(BigInteger, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False)
    ts_utc = Column(DateTime, nullable=False, index=True)
    service = Column(String(50), nullable=False, index=True)  # api, ai, sim
    model = Column(String(50), nullable=True, index=True)  # gpt-4o, claude-3.5
    tokens_in = Column(Integer, default=0)
    tokens_out = Column(Integer, default=0)
    cost_usd = Column(Float, default=0.0)
    meta_json = Column(JSON, nullable=True)  # Request metadata

    # Relationships
    tenant = relationship("Tenant", back_populates="usage_events")

    # Composite indexes for efficient queries
    __table_args__ = (
        Index("idx_usage_tenant_ts", "tenant_id", "ts_utc"),
        Index("idx_usage_tenant_service_ts", "tenant_id", "service", "ts_utc"),
    )


class RateLimit(Base):
    """Rate limiting state per tenant."""

    __tablename__ = "rate_limits"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, nullable=False, index=True)
    window = Column(String(20), nullable=False)  # minute, hour, day
    used = Column(Integer, default=0)
    limit = Column(Integer, nullable=False)
    reset_at = Column(DateTime, nullable=False)

    # Composite index for lookups
    __table_args__ = (Index("idx_tenant_window", "tenant_id", "window"),)


class AuditLog(Base):
    """Audit trail for all actions."""

    __tablename__ = "audit_logs"

    id = Column(BigInteger, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False)
    actor_user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    action = Column(String(100), nullable=False, index=True)
    target = Column(String(200), nullable=True)  # Resource affected
    ts_utc = Column(DateTime, default=lambda: datetime.now(UTC), index=True)
    ip_address = Column(String(45), nullable=True)  # IPv4/IPv6
    meta_json = Column(JSON, nullable=True)  # Additional context

    # Relationships
    tenant = relationship("Tenant", back_populates="audit_logs")
    actor_user = relationship("User", back_populates="audit_logs")

    # Composite indexes
    __table_args__ = (
        Index("idx_audit_tenant_ts", "tenant_id", "ts_utc"),
        Index("idx_audit_tenant_action", "tenant_id", "action"),
    )


class Invoice(Base):
    """Billing invoices from payment providers."""

    __tablename__ = "invoices"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False)
    provider = Column(String(20), nullable=False, index=True)
    external_id = Column(String(100), nullable=False, index=True)
    amount_usd = Column(Float, nullable=False)
    status = Column(String(20), nullable=False, index=True)  # pending, paid, failed
    issued_at = Column(DateTime, nullable=False)
    paid_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(UTC))

    # Relationships
    tenant = relationship("Tenant", back_populates="invoices")

    # Composite index
    __table_args__ = (Index("idx_invoice_provider_external", "provider", "external_id"),)
