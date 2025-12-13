#!/usr/bin/env python3
"""Admin UI Router."""

from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def admin_dashboard():
    """Admin dashboard."""
    return {"message": "Admin UI - implementation coming soon"}
