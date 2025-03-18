#!/bin/bash
# Script to deploy directly on the current VM

set -e  # Exit on any error

echo "===== Starting Deployment ====="

# 1. Update requirements.txt from venv
echo "Updating requirements.txt from venv..."
../venv/bin/pip freeze > requirements.txt

# 2. Clean up Docker to free space (optional)
echo "Cleaning up Docker resources to free space..."
docker system prune -f

# 3. Build the Docker image
echo "Building Docker image..."
docker-compose build fastapi

# 4. Deploy the updated container
echo "Deploying new container..."
docker-compose up -d

# 5. Display status
echo "Deployment complete! Current container status:"
docker-compose ps

echo "===== Deployment Finished ====="
echo "To view logs: docker-compose logs -f fastapi"