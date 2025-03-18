FROM python:3.12-slim as base
WORKDIR /app
# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*
# Copy and install requirements first (better layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Development image with hot reload
FROM base as dev
# We'll mount the app directory as a volume in docker-compose
EXPOSE 8000
CMD ["uvicorn", "app.agents.nl2sql.source.main:app", "--host", "0.0.0.0", "--reload"]

# Production image with code copied in
FROM base as prod
COPY app ./app
EXPOSE 8000
CMD ["uvicorn", "app.agents.nl2sql.source.main:app", "--host", "0.0.0.0"]

# Default target - will be overridden by --build-arg
ARG TARGET=dev
FROM ${TARGET}