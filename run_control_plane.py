#!/usr/bin/env python3
"""
EQ12 Control Plane Startup Script
=================================

SPDX-License-Identifier: MIT
SPDX-FileCopyrightText: 2025 EQ12 Project Contributors

Initializes database and starts the control plane server.
"""

import argparse
import logging
import os
import sys
from pathlib import Path

# Add the parent directory to the path for imports
sys.path.insert(0, str(Path(__file__).parent))

from eq12_control.config import settings
from eq12_control.db import engine, init_db
from eq12_control.models import Membership, Tenant, User

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def init_database():
    """Initialize database with tables."""
    try:
        logger.info("🔧 Initializing database...")
        init_db()
        logger.info("✅ Database initialized successfully")
        return True
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")
        return False


def create_admin_user():
    """Create default admin user if none exists."""
    try:
        from sqlalchemy.orm import sessionmaker

        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db = SessionLocal()

        # Check if any admin user exists
        admin_user = db.query(User).filter(User.is_admin).first()
        if admin_user:
            logger.info(f"📋 Admin user already exists: {admin_user.email}")
            db.close()
            return

        # Create default admin tenant
        admin_tenant = db.query(Tenant).filter(Tenant.name == "admin").first()
        if not admin_tenant:
            admin_tenant = Tenant(
                name="admin", display_name="EQ12 Administration", settings={"is_system": True}
            )
            db.add(admin_tenant)
            db.flush()

        # Create default admin user
        admin_email = os.getenv("EQ12_ADMIN_EMAIL", "admin@eq12.local")
        admin_user = User(
            email=admin_email,
            full_name="EQ12 Administrator",
            is_active=True,
            is_admin=True,
            tenant_id=admin_tenant.id,
        )
        db.add(admin_user)
        db.flush()

        # Create membership
        membership = Membership(
            user_id=admin_user.id, tenant_id=admin_tenant.id, role="owner", is_active=True
        )
        db.add(membership)

        db.commit()
        db.close()

        logger.info(f"✅ Created admin user: {admin_email}")
        logger.info("💡 Use magic link authentication to login")

    except Exception as e:
        logger.error(f"❌ Failed to create admin user: {e}")


def run_server():
    """Start the FastAPI server."""
    try:
        import uvicorn

        logger.info("🚀 Starting EQ12 Control Plane...")
        logger.info(f"📖 API Documentation: http://localhost:{settings.port}/control/docs")
        logger.info(f"💡 Health Check: http://localhost:{settings.port}/control/health")

        uvicorn.run(
            "eq12_control.app:app",
            host=settings.host,
            port=settings.port,
            reload=settings.debug,
            log_level="info",
        )
    except KeyboardInterrupt:
        logger.info("🛑 Server stopped by user")
    except Exception as e:
        logger.error(f"❌ Server failed to start: {e}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="EQ12 Control Plane")
    parser.add_argument(
        "--init-only", action="store_true", help="Initialize database only, don't start server"
    )
    parser.add_argument("--no-admin", action="store_true", help="Skip admin user creation")

    args = parser.parse_args()

    print("🎯 EQ12 Control Plane v1.0.0")
    print("=" * 50)

    # Initialize database
    if not init_database():
        sys.exit(1)

    # Create admin user
    if not args.no_admin:
        create_admin_user()

    # Start server unless init-only
    if not args.init_only:
        run_server()
    else:
        logger.info("✅ Initialization complete")


if __name__ == "__main__":
    main()
