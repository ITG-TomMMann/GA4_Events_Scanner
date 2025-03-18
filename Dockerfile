FROM python:3.12-slim

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

# Copy only what's needed for the application
COPY app ./app

# Expose the port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "app.agents.nl2sql.source.main:app", "--host", "0.0.0.0"]