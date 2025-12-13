#!/usr/bin/env python3
"""Plans Router - Subscription plan management."""

from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def list_plans():
    """List available subscription plans."""
    return {"message": "Plans endpoint - implementation coming soon"}
