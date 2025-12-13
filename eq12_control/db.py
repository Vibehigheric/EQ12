#!/usr/bin/env python3
"""
EQ12 Control Plane Database
==========================

SPDX-License-Identifier: MIT
SPDX-FileCopyrightText: 2025 EQ12 Project Contributors

SQLAlchemy database configuration and session management.
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, sessionmaker

from .config import settings

engine = create_engine(
    settings.database_url,
    echo=settings.database_echo,
    connect_args={"check_same_thread": False} if "sqlite" in settings.database_url else {},
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db() -> Session:
    """Database session dependency for FastAPI."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Initialize database tables."""
    # Import all models to ensure they are registered
    from . import models  # noqa

    try:
        Base.metadata.create_all(bind=engine)
    except Exception as e:
        # If tables already exist, that's okay
        if "already exists" in str(e):
            print(f"Warning: {e}")
        else:
            raise e
