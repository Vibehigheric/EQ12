# EdgeFinder - Secure Docker Environment
# Multi-stage build for minimal attack surface and optimal security

FROM python:3.11-slim-bullseye as builder

# Set build arguments
ARG DEBIAN_FRONTEND=noninteractive

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash --uid 1000 edgefinder

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY pyproject.toml README.md ./
COPY src/ ./src/

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -e .

# Install security scanning tools
RUN pip install --no-cache-dir bandit safety semgrep

# Production stage
FROM python:3.11-slim-bullseye as production

# Set environment variables for security
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    DEBIAN_FRONTEND=noninteractive

# Install runtime dependencies only
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Create non-root user
RUN useradd --create-home --shell /bin/bash --uid 1000 edgefinder

# Create secure directories
RUN mkdir -p /app /data /config /logs && \
    chown -R edgefinder:edgefinder /app /data /config /logs

# Copy Python environment from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code
COPY --chown=edgefinder:edgefinder src/ /app/src/
COPY --chown=edgefinder:edgefinder pyproject.toml /app/
COPY --chown=edgefinder:edgefinder README.md /app/

# Copy configuration templates
COPY --chown=edgefinder:edgefinder configs/example-config.yaml /config/default-config.yaml

# Set working directory and switch to non-root user
WORKDIR /app
USER edgefinder

# Install application in development mode
RUN pip install --user --no-cache-dir -e .

# Add user's local bin to PATH
ENV PATH="/home/edgefinder/.local/bin:$PATH"

# Set secure default configuration
ENV EDGEFINDER_CONFIG_PATH=/config/edgefinder-config.yaml \
    EDGEFINDER_OUTPUT_DIR=/data/output \
    EDGEFINDER_DOWNLOADS_DIR=/data/downloads \
    EDGEFINDER_LOG_LEVEL=INFO

# Create default directories
RUN mkdir -p /data/output /data/downloads /data/reports

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import edgefinder; print('EdgeFinder is healthy')" || exit 1

# Security: Run as non-root, read-only root filesystem
USER edgefinder
VOLUME ["/data", "/config", "/logs"]

# Default command
ENTRYPOINT ["python", "-m", "edgefinder.cli"]
CMD ["--help"]

# Labels for metadata
LABEL org.opencontainers.image.title="EdgeFinder" \
      org.opencontainers.image.description="Ethical Repository Reconnaissance Tool for EQ12" \
      org.opencontainers.image.version="1.0.0" \
      org.opencontainers.image.vendor="EQ12 Development Team" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.documentation="https://github.com/eq12/edgefinder" \
      maintainer="EQ12 Development Team"