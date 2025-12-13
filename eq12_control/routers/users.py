#!/usr/bin/env python3
"""User Management Router."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import AuditLog, User
from ..schemas import UserResponse, UserUpdateRequest
from .auth import get_current_active_user

router = APIRouter()


@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(current_user: User = Depends(get_current_active_user)):
    """Get current user profile."""
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        full_name=current_user.full_name,
        is_active=current_user.is_active,
        is_admin=current_user.is_admin,
        created_at=current_user.created_at,
        last_login=current_user.last_login,
    )


@router.put("/me", response_model=UserResponse)
async def update_current_user(
    request: UserUpdateRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Update current user profile."""
    update_data = request.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(current_user, field, value)

    # Log update
    audit_log = AuditLog(
        user_id=current_user.id,
        action="user_updated",
        resource="user",
        details={"updated_fields": list(update_data.keys())},
    )
    db.add(audit_log)

    db.commit()

    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        full_name=current_user.full_name,
        is_active=current_user.is_active,
        is_admin=current_user.is_admin,
        created_at=current_user.created_at,
        last_login=current_user.last_login,
    )
