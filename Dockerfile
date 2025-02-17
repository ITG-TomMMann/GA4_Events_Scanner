FROM python:3.9-slim

# Ensure working directory is set correctly
WORKDIR /app/nl2sql
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1


# Install dependencies
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copy project
COPY . .

# Run the application
ENTRYPOINT ["python", "source/main.py"]
