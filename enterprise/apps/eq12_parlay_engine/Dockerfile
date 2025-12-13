FROM python:3.12-slim

LABEL maintainer="EQ12 Enterprise Team"
LABEL description="EQ12 Parlay Engine - Enterprise FastAPI Service"

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy EQ12 betting engines (will be mounted from host)
COPY main.py ./
COPY config/ ./config/

# Create directories for EQ12 integration
RUN mkdir -p /eq12scripts /eq12configs /eq12logs

# Environment variables
ENV PYTHONPATH="/app:/eq12scripts"
ENV EQ12_CONFIG_PATH="/eq12configs/eq12_master_config.json"
ENV OTEL_EXPORTER_OTLP_ENDPOINT="http://otel-collector:4317"
ENV OTEL_SERVICE_NAME="eq12-parlay-engine"

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# Expose port
EXPOSE 8080

# Run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080", "--workers", "1"]