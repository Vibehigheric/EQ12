FROM python:3.11-slim

WORKDIR /app

# Set proxy for apt and pip
ENV http_proxy=http://127.0.0.1:8888
ENV https_proxy=http://127.0.0.1:8888

# Install system dependencies for psycopg2
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies
RUN pip install psycopg2-binary requests

# Copy source code
COPY . /app

CMD ["python", "ingest.py"]
