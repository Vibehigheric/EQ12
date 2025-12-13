# EQ12 GODSTACK Dockerfile
# Optimized for Swarm & BuildKit

FROM python:3.12-slim AS base

# Set environment vars
ENV PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1 \
    PATH="/home/appuser/.local/bin:$PATH"

# System dependencies
RUN apt-get update && export DEBIAN_FRONTEND=noninteractive \
    && apt-get install -y --no-install-recommends \
    build-essential \
    curl wget unzip git \
    libnss3 libatk-bridge2.0-0 libxkbcommon0 libdrm2 \
    libxcomposite1 libxrandr2 libgbm1 libasound2 xvfb \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements first for caching
COPY requirements.txt .

# Install Python dependencies AS ROOT
# This fixes the [Errno 13] Permission denied errors
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright and other tools AS ROOT
RUN pip install --no-cache-dir playwright==1.47.0 fastapi uvicorn && \
    playwright install --with-deps chromium

# Create non-root user
RUN useradd --create-home --shell /bin/bash appuser
RUN chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Copy app source
COPY --chown=appuser:appuser . .

# Create data directory for SQLite and logs
RUN mkdir -p /app/data /app/logs

# Healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD python scripts/multi_provider_ai_router.py --health-check || exit 1

# Default Command
CMD ["python", "scripts/eq12_master_orchestrator.py"]

# Expose port for dashboard
EXPOSE 8000
