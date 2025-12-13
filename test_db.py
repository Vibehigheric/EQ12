#!/usr/bin/env python3
"""Test database initialization."""

import sys
from pathlib import Path

# Add the parent directory to the path for imports
sys.path.insert(0, str(Path(__file__).parent))

from eq12_control.db import Base, engine

# Import all models explicitly


def test_db_creation():
    """Test database table creation."""
    print("Creating all tables...")

    # Drop all tables first
    Base.metadata.drop_all(bind=engine)
    print("Dropped all existing tables")

    # Create all tables
    Base.metadata.create_all(bind=engine)
    print("Created all tables successfully")

    # Show table names
    from sqlalchemy import inspect

    inspector = inspect(engine)
    tables = inspector.get_table_names()

    print("Created tables:")
    for table in tables:
        print(f"  - {table}")


if __name__ == "__main__":
    test_db_creation()
