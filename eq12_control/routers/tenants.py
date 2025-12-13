#!/usr/bin/env python3
"""
Tenant Management Router for EQ12 Control Plane
===============================================

Handles tenant (organization) management operations.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import AuditLog, Membership, Tenant, User
from ..schemas import (
    TenantCreateRequest,
    TenantCreateResponse,
    TenantResponse,
    TenantUpdateRequest,
    UserInviteRequest,
    UserInviteResponse,
)
from .auth import get_current_active_user

router = APIRouter()


@router.post("/", response_model=TenantCreateResponse, status_code=status.HTTP_201_CREATED)
async def create_tenant(
    request: TenantCreateRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Create a new tenant (organization)."""
    # Check if user can create tenants (admin only for now)
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Only admins can create tenants"
        )

    # Check if tenant name is unique
    existing_tenant = db.query(Tenant).filter(Tenant.name == request.name).first()
    if existing_tenant:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Tenant name already exists"
        )

    # Create tenant
    tenant = Tenant(
        name=request.name, display_name=request.display_name, settings=request.settings or {}
    )
    db.add(tenant)
    db.flush()

    # Create membership for current user as owner
    membership = Membership(user_id=current_user.id, tenant_id=tenant.id, role="owner")
    db.add(membership)

    # Log tenant creation
    audit_log = AuditLog(
        user_id=current_user.id,
        tenant_id=tenant.id,
        action="tenant_created",
        resource="tenant",
        details={"tenant_name": tenant.name, "created_by": current_user.email},
    )
    db.add(audit_log)

    db.commit()

    return TenantCreateResponse(
        id=tenant.id,
        name=tenant.name,
        display_name=tenant.display_name,
        created_at=tenant.created_at,
    )


@router.get("/", response_model=list[TenantResponse])
async def list_tenants(
    current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)
):
    """List all tenants for current user."""
    # Get tenants where user is a member
    tenants_query = db.query(Tenant).join(Membership).filter(Membership.user_id == current_user.id)

    # If admin, show all tenants
    if current_user.is_admin:
        tenants_query = db.query(Tenant)

    tenants = tenants_query.all()

    return [
        TenantResponse(
            id=tenant.id,
            name=tenant.name,
            display_name=tenant.display_name,
            created_at=tenant.created_at,
            is_active=tenant.is_active,
            user_count=db.query(func.count(Membership.user_id))
            .filter(Membership.tenant_id == tenant.id)
            .scalar(),
        )
        for tenant in tenants
    ]


@router.get("/{tenant_id}", response_model=TenantResponse)
async def get_tenant(
    tenant_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Get tenant details."""
    # Check if user has access to tenant
    membership = (
        db.query(Membership)
        .filter(Membership.user_id == current_user.id, Membership.tenant_id == tenant_id)
        .first()
    )

    if not membership and not current_user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if not tenant:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tenant not found")

    return TenantResponse(
        id=tenant.id,
        name=tenant.name,
        display_name=tenant.display_name,
        created_at=tenant.created_at,
        is_active=tenant.is_active,
        user_count=db.query(func.count(Membership.user_id))
        .filter(Membership.tenant_id == tenant.id)
        .scalar(),
    )


@router.put("/{tenant_id}", response_model=TenantResponse)
async def update_tenant(
    tenant_id: str,
    request: TenantUpdateRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Update tenant settings."""
    # Check if user is owner or admin
    membership = (
        db.query(Membership)
        .filter(Membership.user_id == current_user.id, Membership.tenant_id == tenant_id)
        .first()
    )

    if not membership or (membership.role != "owner" and not current_user.is_admin):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Only tenant owners can update settings"
        )

    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if not tenant:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tenant not found")

    # Update fields
    update_data = request.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(tenant, field, value)

    # Log update
    audit_log = AuditLog(
        user_id=current_user.id,
        tenant_id=tenant.id,
        action="tenant_updated",
        resource="tenant",
        details={"updated_fields": list(update_data.keys()), "updated_by": current_user.email},
    )
    db.add(audit_log)

    db.commit()

    return TenantResponse(
        id=tenant.id,
        name=tenant.name,
        display_name=tenant.display_name,
        created_at=tenant.created_at,
        is_active=tenant.is_active,
        user_count=db.query(func.count(Membership.user_id))
        .filter(Membership.tenant_id == tenant.id)
        .scalar(),
    )


@router.post("/{tenant_id}/invite", response_model=UserInviteResponse)
async def invite_user(
    tenant_id: str,
    request: UserInviteRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Invite a user to join the tenant."""
    # Check if user can invite (owner or admin role)
    membership = (
        db.query(Membership)
        .filter(Membership.user_id == current_user.id, Membership.tenant_id == tenant_id)
        .first()
    )

    if not membership or membership.role not in ["owner", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Only owners and admins can invite users"
        )

    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if not tenant:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tenant not found")

    # Check if user already exists
    existing_user = db.query(User).filter(User.email == request.email).first()
    if existing_user:
        # Check if already a member
        existing_membership = (
            db.query(Membership)
            .filter(Membership.user_id == existing_user.id, Membership.tenant_id == tenant_id)
            .first()
        )

        if existing_membership:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail="User is already a member"
            )

    # Create user if doesn't exist
    if not existing_user:
        user = User(
            email=request.email,
            full_name=request.full_name or "",
            is_active=False,  # Will be activated when they accept invite
        )
        db.add(user)
        db.flush()
        user_id = user.id
    else:
        user_id = existing_user.id

    # Create membership
    new_membership = Membership(
        user_id=user_id,
        tenant_id=tenant_id,
        role=request.role,
        is_active=False,  # Will be activated when they accept
    )
    db.add(new_membership)

    # In production, send invitation email here
    # For now, just log the invitation
    audit_log = AuditLog(
        user_id=current_user.id,
        tenant_id=tenant_id,
        action="user_invited",
        resource="membership",
        details={
            "invited_email": request.email,
            "role": request.role,
            "invited_by": current_user.email,
        },
    )
    db.add(audit_log)

    db.commit()

    return UserInviteResponse(
        message="User invited successfully", email=request.email, role=request.role
    )
