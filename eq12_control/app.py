#!/usr/bin/env python3
"""
EQ12 Control Plane FastAPI Application
=====================================

SPDX-License-Identifier: MIT
SPDX-FileCopyrightText: 2025 EQ12 Project Contributors

Production-ready multi-tenant SaaS control plane.
"""

import time
import uuid
from contextlib import asynccontextmanager
from datetime import UTC, datetime

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from .config import settings
from .db import init_db
from .routers import (
    admin,
    api_keys,
    audit,
    auth,
    billing,
    licensing,
    limits,
    plans,
    tenants,
    usage,
    users,
)
from .schemas import HealthResponse

# Prometheus metrics
REQUEST_COUNT = Counter(
    "eq12_control_requests_total",
    "Total requests to control plane",
    ["method", "endpoint", "status"],
)

REQUEST_DURATION = Histogram(
    "eq12_control_request_duration_seconds", "Request duration in seconds", ["method", "endpoint"]
)

# Rate limiter
limiter = Limiter(key_func=get_remote_address)

# Startup time for health checks
startup_time = time.time()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management."""
    # Startup
    print("🚀 EQ12 Control Plane starting up...")
    init_db()
    print("📊 Database initialized")
    print("🔐 Security: JWT enabled")
    print(f"🌐 CORS origins: {settings.cors_origins}")
    yield
    # Shutdown
    print("🛑 EQ12 Control Plane shutting down...")


# Create FastAPI app
app = FastAPI(
    title="EQ12 Control Plane",
    description="Multi-tenant SaaS platform for EQ12 betting mathematics",
    version="1.0.0",
    docs_url="/control/docs",
    redoc_url="/control/redoc",
    openapi_url="/control/openapi.json",
    lifespan=lifespan,
)

# Add rate limiting
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS middleware
if settings.cors_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=settings.cors_allow_credentials,
        allow_methods=["*"],
        allow_headers=["*"],
    )


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """Add request timing and metrics."""
    start_time = time.time()

    # Add request ID
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id

    try:
        response = await call_next(request)
        process_time = time.time() - start_time

        # Add headers
        response.headers["X-Process-Time"] = str(process_time)
        response.headers["X-Request-ID"] = request_id

        # Prometheus metrics
        REQUEST_COUNT.labels(
            method=request.method, endpoint=request.url.path, status=response.status_code
        ).inc()

        REQUEST_DURATION.labels(method=request.method, endpoint=request.url.path).observe(
            process_time
        )

        return response

    except Exception as e:
        process_time = time.time() - start_time

        # Count errors
        REQUEST_COUNT.labels(method=request.method, endpoint=request.url.path, status=500).inc()

        raise e


# Health check endpoint
@app.get("/control/health", response_model=HealthResponse)
@limiter.limit("10/minute")
async def health_check(request: Request):
    """Health check endpoint for monitoring."""
    try:
        # Test database connection
        from .db import engine

        with engine.connect() as conn:
            conn.execute("SELECT 1")
        database_ok = True
    except Exception:
        database_ok = False

    return HealthResponse(
        status="ok" if database_ok else "degraded",
        database=database_ok,
        uptime_seconds=time.time() - startup_time,
    )


# Metrics endpoint
@app.get("/control/metrics")
async def metrics():
    """Prometheus metrics endpoint."""
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)


# Include routers with /control/api prefix
app.include_router(auth.router, prefix="/control/api/auth", tags=["Authentication"])
app.include_router(tenants.router, prefix="/control/api/tenants", tags=["Tenants"])
app.include_router(users.router, prefix="/control/api/users", tags=["Users"])
app.include_router(api_keys.router, prefix="/control/api/keys", tags=["API Keys"])
app.include_router(plans.router, prefix="/control/api/plans", tags=["Plans"])
app.include_router(billing.router, prefix="/control/api/billing", tags=["Billing"])
app.include_router(usage.router, prefix="/control/api/usage", tags=["Usage"])
app.include_router(limits.router, prefix="/control/api/limits", tags=["Limits"])
app.include_router(licensing.router, prefix="/control/api/license", tags=["Licensing"])
app.include_router(audit.router, prefix="/control/api/audit", tags=["Audit"])
app.include_router(admin.router, prefix="/control/admin", tags=["Admin"])


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Custom HTTP exception handler with request ID."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": exc.detail,
            "request_id": getattr(request.state, "request_id", "unknown"),
            "timestamp": datetime.now(UTC).isoformat(),
        },
    )


# Root redirect
@app.get("/control")
async def control_root():
    """Redirect to documentation."""
    from fastapi.responses import RedirectResponse

    return RedirectResponse(url="/control/docs")


if __name__ == "__main__":
    import uvicorn

    print("🚀 Starting EQ12 Control Plane in development mode...")
    print("📖 API Documentation: http://localhost:8001/control/docs")
    print("💡 Health Check: http://localhost:8001/control/health")

    uvicorn.run("eq12_control.app:app", host="0.0.0.0", port=8001, reload=True, log_level="info")
