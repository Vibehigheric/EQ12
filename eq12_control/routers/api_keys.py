#!/usr/bin/env python3
"""API Key Management Router."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import APIKey, AuditLog, User
from ..schemas import APIKeyCreateRequest, APIKeyCreateResponse, APIKeyResponse
from ..security import SecurityManager
from .auth import get_current_active_user

router = APIRouter()
security_manager = SecurityManager()


@router.post("/", response_model=APIKeyCreateResponse, status_code=status.HTTP_201_CREATED)
async def create_api_key(
    request: APIKeyCreateRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Create a new API key."""
    # Generate API key
    key_value = security_manager.generate_api_key()
    key_hash = security_manager.hash_api_key(key_value)

    # Create API key record
    api_key = APIKey(
        user_id=current_user.id,
        tenant_id=current_user.tenant_id,
        name=request.name,
        key_hash=key_hash,
        scopes=request.scopes or ["read"],
    )
    db.add(api_key)

    # Log creation
    audit_log = AuditLog(
        user_id=current_user.id,
        tenant_id=current_user.tenant_id,
        action="api_key_created",
        resource="api_key",
        details={"key_name": request.name, "scopes": api_key.scopes},
    )
    db.add(audit_log)

    db.commit()

    return APIKeyCreateResponse(
        id=api_key.id,
        name=api_key.name,
        key=key_value,  # Only shown once
        scopes=api_key.scopes,
        created_at=api_key.created_at,
    )


@router.get("/", response_model=list[APIKeyResponse])
async def list_api_keys(
    current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)
):
    """List user's API keys."""
    keys = db.query(APIKey).filter(APIKey.user_id == current_user.id, APIKey.is_active).all()

    return [
        APIKeyResponse(
            id=key.id,
            name=key.name,
            scopes=key.scopes,
            created_at=key.created_at,
            last_used=key.last_used,
            is_active=key.is_active,
        )
        for key in keys
    ]


@router.delete("/{key_id}")
async def delete_api_key(
    key_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Delete an API key."""
    api_key = (
        db.query(APIKey).filter(APIKey.id == key_id, APIKey.user_id == current_user.id).first()
    )

    if not api_key:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="API key not found")

    # Soft delete
    api_key.is_active = False

    # Log deletion
    audit_log = AuditLog(
        user_id=current_user.id,
        tenant_id=current_user.tenant_id,
        action="api_key_deleted",
        resource="api_key",
        details={"key_name": api_key.name},
    )
    db.add(audit_log)

    db.commit()

    return {"message": "API key deleted successfully"}
