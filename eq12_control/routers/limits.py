#!/usr/bin/env python3
"""Rate Limits Router."""

from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def get_limits():
    """Get rate limits."""
    return {"message": "Rate limits - implementation coming soon"}
