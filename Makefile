.PHONY: setup build build-no-cache start start-with-admin dev-build dev-start stop clean logs db-shell db-backup db-restore test help

# Default environment
ENV_FILE ?= .env
include $(ENV_FILE)
export

# Project name
PROJECT_NAME = nl2sql

# Setup project directories
setup:
	@echo "Creating necessary directories..."
	mkdir -p postgres/init
	mkdir -p app/agents/nl2sql/source/utils
	cp -n postgres/init/01-schema.sql postgres/init/ 2>/dev/null || true
	cp -n postgres/init/02-test-data.sql postgres/init/ 2>/dev/null || true
	@echo "Setup complete!"

# Development build (faster for development)
dev-build:
	@echo "Building minimal Docker containers for development..."
	COMPOSE_DOCKER_CLI_BUILD=1 DOCKER_BUILDKIT=1 docker-compose build

build:
	@echo "Building Docker containers..."
	COMPOSE_DOCKER_CLI_BUILD=1 DOCKER_BUILDKIT=1 docker-compose build

# Force rebuild with no cache
build-no-cache:
	@echo "Building Docker containers without cache..."
	COMPOSE_DOCKER_CLI_BUILD=1 DOCKER_BUILDKIT=1 docker-compose build --no-cache

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

# Show help
help:
	@echo "Available commands:"
	@echo "  make setup              - Create necessary directories and files"
	@echo "  make dev-build          - Build Docker containers for development (faster)"
	@echo "  make build              - Build Docker containers for production"
	@echo "  make build-no-cache     - Build Docker containers without using cache"
	@echo "  make start              - Start essential services in detached mode"
	@echo "  make start-with-admin   - Start all services including pgAdmin"
	@echo "  make dev-start          - Start development environment with hot reload"
	@echo "  make run                - Start all services in foreground (with logs)"
	@echo "  make stop               - Stop all services"
	@echo "  make clean              - Stop services and remove volumes"
	@echo "  make logs               - View logs for all services"
	@echo "  make api-logs           - View FastAPI logs"
	@echo "  make db-logs            - View PostgreSQL logs"
	@echo "  make db-shell           - Open PostgreSQL shell"
	@echo "  make db-backup          - Backup the database"
	@echo "  make db-restore FILE=backups/file.sql - Restore the database from backup"
	@echo "  make test               - Run tests"
	@echo "  make prune              - Clean up unused Docker resources"
	@echo "  make help               - Show this help message"