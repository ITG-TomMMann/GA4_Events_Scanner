.PHONY: build deploy restart logs status cleanup help

# Simple direct deployment on the current VM

# Build container
build:
	@echo "Building Docker image..."
	../venv/bin/pip freeze > requirements.txt
	docker-compose build fastapi

# Deploy (build and start)
deploy: build
	@echo "Deploying new container..."
	docker-compose up -d
	@echo "Deployment complete!"

# Restart without rebuilding
restart:
	@echo "Restarting containers..."
	docker-compose restart fastapi
	@echo "Restart complete!"

# View logs
logs:
	@echo "Viewing logs..."
	docker-compose logs -f fastapi

# Check status
status:
	@echo "Current container status:"
	docker-compose ps

# Clean up Docker resources
cleanup:
	@echo "Cleaning up Docker resources..."
	docker system prune -f
	@echo "Cleanup complete!"

# Full deployment with cleanup
full-deploy: cleanup build deploy

# Show help
help:
	@echo "Deployment Commands:"
	@echo "  make -f Makefile.fixed build      - Build the Docker image"
	@echo "  make -f Makefile.fixed deploy     - Build and deploy"
	@echo "  make -f Makefile.fixed restart    - Restart without rebuilding"
	@echo "  make -f Makefile.fixed logs       - View container logs"
	@echo "  make -f Makefile.fixed status     - Check container status"
	@echo "  make -f Makefile.fixed cleanup    - Clean Docker resources"
	@echo "  make -f Makefile.fixed full-deploy- Cleanup, build and deploy"