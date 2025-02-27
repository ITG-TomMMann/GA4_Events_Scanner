FROM python:3.9-slim

# 1. Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 2. Set working directory in the container
WORKDIR /app

# 3. Copy and install dependencies
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# 4. Copy all project files into the container
COPY . .

# 5. Expose port (for documentation; Cloud Run sets the actual PORT at runtime)
EXPOSE 8000

# 6. Command to run the FastAPI application
#    Using uvicorn here to serve FastAPI, referencing your module path: 
#    "app.agents.nl2sql.source.main:app"
CMD ["sh", "-c", "uvicorn app.agents.nl2sql.source.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
