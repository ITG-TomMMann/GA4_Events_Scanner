.PHONY: setup dev-build build build-no-cache start start-with-admin dev-start run stop clean logs api-logs db-logs db-shell db-backup db-restore test prune prod-build image-save deploy-prod deploy-code-only ssh-setup help

# Default environment
ENV_FILE ?= .env
include $(ENV_FILE)
export

# Project name
PROJECT_NAME = nl2sql

# Production VM settings (customize these)
PROD_VM ?= user@your-server.example.com
PROD_PATH ?= /path/to/project

# Setup project directories
setup:
	@echo "Creating necessary directories..."
	mkdir -p postgres/init
	mkdir -p app/agents/nl2sql/source/utils
	mkdir -p deploy
	cp -n postgres/init/01-schema.sql postgres/init/ 2>/dev/null || true
	cp -n postgres/init/02-test-data.sql postgres/init/ 2>/dev/null || true
	@echo "Setup complete!"

# Development build (faster for development)
dev-build:
	@echo "Building minimal Docker containers for development..."
	COMPOSE_DOCKER_CLI_BUILD=1 DOCKER_BUILDKIT=1 docker-compose build --build-arg TARGET=dev

# Production build
build:
	@echo "Building Docker containers..."
	COMPOSE_DOCKER_CLI_BUILD=1 DOCKER_BUILDKIT=1 docker-compose build --build-arg TARGET=prod

# Force rebuild with no cache
build-no-cache:
	@echo "Building Docker containers without cache..."
	COMPOSE_DOCKER_CLI_BUILD=1 DOCKER_BUILDKIT=1 docker-compose build --no-cache --build-arg TARGET=prod

# Start all services without pgAdmin
start:
	@echo "Starting essential services..."
	docker-compose up -d
	@echo "Services started! FastAPI available at http://localhost:8000"

# Start all services with pgAdmin
start-with-admin:
	@echo "Starting all services including pgAdmin..."
	docker-compose --profile admin up -d
	@echo "Services started! FastAPI available at http://localhost:8000, pgAdmin at http://localhost:5050"

# Development start (with file watching)
dev-start:
	@echo "Starting development environment..."
	docker-compose up -d
	@echo "Development environment started! FastAPI available at http://localhost:8000 with hot reload"

# Start all services in foreground (with logs)
run:
	@echo "Starting all services in foreground mode..."
	docker-compose up

# Stop all services
stop:
	@echo "Stopping all services..."
	docker-compose down

# Stop services and remove volumes
clean:
	@echo "Stopping services and removing volumes..."
	docker-compose down -v

# View logs
logs:
	docker-compose logs -f

# FastAPI logs specifically
api-logs:
	docker-compose logs -f fastapi

# Database logs specifically
db-logs:
	docker-compose logs -f postgres

# Shell into PostgreSQL
db-shell:
	docker exec -it nl2sql_postgres psql -U nl2sql_user -d nl2sql_db

# Backup the database
db-backup:
	@echo "Creating database backup..."
	mkdir -p backups
	docker exec -t nl2sql_postgres pg_dump -U nl2sql_user nl2sql_db > backups/nl2sql_db_$(shell date +%Y%m%d_%H%M%S).sql
	@echo "Backup created in backups/ directory!"

# Restore the database (usage: make db-restore FILE=backups/filename.sql)
db-restore:
	@if [ -z "$(FILE)" ]; then \
		echo "Error: Please specify the backup file. Usage: make db-restore FILE=backups/filename.sql"; \
		exit 1; \
	fi
	@echo "Restoring database from $(FILE)..."
	cat $(FILE) | docker exec -i nl2sql_postgres psql -U nl2sql_user -d nl2sql_db
	@echo "Restore complete!"

# Run tests
test:
	docker exec nl2sql_api pytest

# Prune Docker system
prune:
	@echo "Cleaning up unused Docker resources..."
	docker system prune -f

# Build production image
prod-build:
	@echo "Building standalone production Docker image..."
	docker build --target prod -t $(PROJECT_NAME):latest .

# Save Docker image to file
image-save:
	@echo "Saving Docker image to file..."
	mkdir -p deploy
	docker save $(PROJECT_NAME):latest | gzip > deploy/$(PROJECT_NAME)-latest.tar.gz
	@echo "Image saved to deploy/$(PROJECT_NAME)-latest.tar.gz"

# Deploy to production VM (requires SSH access)
deploy-prod: prod-build image-save
	@echo "Deploying to production VM..."
	scp deploy/$(PROJECT_NAME)-latest.tar.gz $(PROD_VM):/tmp/
	ssh $(PROD_VM) "gunzip -c /tmp/$(PROJECT_NAME)-latest.tar.gz | docker load && \
		cd $(PROD_PATH) && \
		docker-compose stop fastapi && \
		docker-compose up -d fastapi"
	@echo "Deployment complete!"

# Quick deploy (only code changes)
deploy-code-only:
	@echo "Deploying only code changes to production VM..."
	tar -czf deploy/app-code.tar.gz app
	scp deploy/app-code.tar.gz $(PROD_VM):/tmp/
	ssh $(PROD_VM) "cd $(PROD_PATH) && \
		tar -xzf /tmp/app-code.tar.gz -C . && \
		docker-compose restart fastapi"
	@echo "Code deployment complete!"

# Setup SSH for password-less deployment
ssh-setup:
	@echo "Setting up SSH keys for password-less deployment..."
	@if [ ! -f ~/.ssh/id_rsa ]; then \
		ssh-keygen -t rsa -b 4096 -f ~/.ssh/id_rsa -N ""; \
	fi
	@echo "Copying SSH key to production server $(PROD_VM)..."
	ssh-copy-id $(PROD_VM)
	@echo "SSH setup complete!"

# Show help
help:
	@echo "NL2SQL Project Makefile Commands:"
	@echo ""
	@echo "=== INITIAL SETUP ==="
	@echo "  make setup              - Create necessary directories and files"
	@echo "  make ssh-setup          - Setup SSH keys for password-less deployment"
	@echo ""
	@echo "=== DEVELOPMENT WORKFLOW ==="
	@echo "  make dev-build          - Build Docker containers for development (faster)"
	@echo "  make dev-start          - Start development environment with hot reload"
	@echo "  make api-logs           - View FastAPI logs while developing"
	@echo ""
	@echo "=== TESTING ==="
	@echo "  make test               - Run automated tests"
	@echo "  make start-with-admin   - Start all services including pgAdmin for DB inspection"
	@echo "  make db-shell           - Open PostgreSQL shell for manual queries"
	@echo ""
	@echo "=== PRODUCTION DEPLOYMENT ==="
	@echo "  make prod-build         - Build production-ready Docker image"
	@echo "  make deploy-prod        - Full deployment (image + dependencies) to production VM"
	@echo "  make deploy-code-only   - Fast deployment (code changes only) to production VM"
	@echo ""
	@echo "=== DATABASE OPERATIONS ==="
	@echo "  make db-backup          - Backup the database"
	@echo "  make db-restore FILE=backups/file.sql - Restore database from backup"
	@echo ""
	@echo "=== MAINTENANCE ==="
	@echo "  make build              - Build Docker containers for production"
	@echo "  make build-no-cache     - Build Docker containers without using cache"
	@echo "  make start              - Start essential services in detached mode"
	@echo "  make run                - Start all services in foreground (with logs)"
	@echo "  make stop               - Stop all services"
	@echo "  make clean              - Stop services and remove volumes"
	@echo "  make logs               - View logs for all services"
	@echo "  make db-logs            - View PostgreSQL logs"
	@echo "  make prune              - Clean up unused Docker resources"