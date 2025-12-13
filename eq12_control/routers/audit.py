#!/usr/bin/env python3
"""Audit Router."""

from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def get_audit_logs():
    """Get audit logs."""
    return {"message": "Audit logs - implementation coming soon"}
