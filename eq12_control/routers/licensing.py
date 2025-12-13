#!/usr/bin/env python3
"""Licensing Router."""

from fastapi import APIRouter

router = APIRouter()


@router.get("/validate")
async def validate_license():
    """Validate license."""
    return {"message": "License validation - implementation coming soon"}
