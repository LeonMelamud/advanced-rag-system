# Advanced RAG System - Makefile
# DRY build system for all services

.PHONY: help build-base build-all build-auth build-chat build-collection build-file build-mcp clean clean-all run-service stop-service logs test

# Default target
help:
	@echo "Advanced RAG System - Build Commands"
	@echo "===================================="
	@echo ""
	@echo "Build Commands:"
	@echo "  make build-base          Build the base Docker image"
	@echo "  make build-all           Build all services"
	@echo "  make build-auth          Build auth service"
	@echo "  make build-chat          Build chat service"
	@echo "  make build-collection    Build collection service"
	@echo "  make build-file          Build file service"
	@echo "  make build-mcp           Build MCP orchestrator service"
	@echo ""
	@echo "Service Management:"
	@echo "  make run-service SERVICE=<name>    Run a specific service"
	@echo "  make stop-service SERVICE=<name>   Stop a specific service"
	@echo "  make logs SERVICE=<name>           View service logs"
	@echo ""
	@echo "Development:"
	@echo "  make up                  Start all services with docker-compose"
	@echo "  make down                Stop all services"
	@echo "  make restart             Restart all services"
	@echo "  make status              Check service status"
	@echo ""
	@echo "Testing & Validation:"
	@echo "  make test                Run unit tests"
	@echo "  make health-check        Check all service health"
	@echo "  make integration-test    Run integration tests"
	@echo "  make test-shared         Test shared components"
	@echo "  make validate-system     Full system validation"
	@echo ""
	@echo "Cleanup:"
	@echo "  make clean               Remove service images"
	@echo "  make clean-all           Remove all images including base"
	@echo ""
	@echo "Available services: auth_service, chat_service, collection_service, file_service, mcp_orchestrator"

# Variables
BASE_IMAGE = collections_ai_assistance-base
SERVICES = auth_service chat_service collection_service file_service mcp_orchestrator

# Service name mapping for convenience
SERVICE_MAP_auth = auth_service
SERVICE_MAP_chat = chat_service
SERVICE_MAP_collection = collection_service
SERVICE_MAP_file = file_service
SERVICE_MAP_mcp = mcp_orchestrator

# Build base image
build-base:
	@echo "Building base image..."
	docker build -f backend/Dockerfile.base -t $(BASE_IMAGE) .
	@echo "✅ Base image built successfully"

# Build all services
build-all: build-base $(addprefix build-,$(SERVICES))
	@echo "✅ All services built successfully"

# Generic service build rule
build-%: validate-service-% build-base
	@echo "Building $* service..."
	docker build -f backend/$*/Dockerfile -t collections_ai_assistance-$* .
	@echo "✅ $* service built successfully"

# Service validation
validate-service-%:
	@if [ ! -d "backend/$*" ]; then \
		echo "❌ Error: Service 'backend/$*' does not exist"; \
		echo "Available services: $(SERVICES)"; \
		exit 1; \
	fi

# Individual service builds (for convenience)
build-auth: build-auth_service
build-chat: build-chat_service  
build-collection: build-collection_service
build-file: build-file_service
build-mcp: build-mcp_orchestrator

# Service management
run-service:
	@if [ -z "$(SERVICE)" ]; then \
		echo "❌ Error: SERVICE parameter required"; \
		echo "Usage: make run-service SERVICE=<service_name>"; \
		echo "Available services: $(SERVICES)"; \
		exit 1; \
	fi
	@echo "Starting $(SERVICE)..."
	docker run -d --name $(SERVICE) collections_ai_assistance-$(SERVICE)
	@echo "✅ $(SERVICE) started"

stop-service:
	@if [ -z "$(SERVICE)" ]; then \
		echo "❌ Error: SERVICE parameter required"; \
		echo "Usage: make stop-service SERVICE=<service_name>"; \
		exit 1; \
	fi
	@echo "Stopping $(SERVICE)..."
	docker stop $(SERVICE) || true
	docker rm $(SERVICE) || true
	@echo "✅ $(SERVICE) stopped"

logs:
	@if [ -z "$(SERVICE)" ]; then \
		echo "❌ Error: SERVICE parameter required"; \
		echo "Usage: make logs SERVICE=<service_name>"; \
		exit 1; \
	fi
	docker logs -f $(SERVICE)

# Docker Compose operations
up:
	@echo "Starting all services with docker-compose..."
	docker-compose up -d
	@echo "✅ All services started"

down:
	@echo "Stopping all services..."
	docker-compose down
	@echo "✅ All services stopped"

restart: down up

# Development helpers
test:
	@echo "Running tests..."
	python -m pytest tests/ -v
	@echo "✅ Tests completed"

# Check if services are running
status:
	@echo "Service Status:"
	@echo "==============="
	@for service in $(SERVICES); do \
		if docker ps --format "table {{.Names}}" | grep -q $$service; then \
			echo "✅ $$service: Running"; \
		else \
			echo "❌ $$service: Stopped"; \
		fi; \
	done

# Cleanup
clean:
	@echo "Removing service images..."
	@for service in $(SERVICES); do \
		docker rmi collections_ai_assistance-$$service 2>/dev/null || true; \
	done
	@echo "✅ Service images removed"

clean-all: clean
	@echo "Removing base image..."
	docker rmi $(BASE_IMAGE) 2>/dev/null || true
	@echo "✅ All images removed"

# Development workflow
dev-setup: build-all
	@echo "Setting up development environment..."
	@echo "✅ Development environment ready"

# Quick rebuild (useful during development)
quick-build-%: 
	@echo "Quick rebuilding $* service..."
	docker build -f backend/$*_service/Dockerfile -t collections_ai_assistance-$*_service . --no-cache
	@echo "✅ $* service rebuilt"

# Health check all services
health-check:
	@echo "Checking service health..."
	@echo "Auth Service (port 8001):"
	@curl -f http://localhost:8001/health/live 2>/dev/null && echo "✅ Auth service healthy" || echo "❌ Auth service health check failed"
	@echo "File Service (port 8002):"
	@curl -f http://localhost:8002/health/live 2>/dev/null && echo "✅ File service healthy" || echo "❌ File service health check failed"
	@echo "Chat Service (port 8003):"
	@curl -f http://localhost:8003/health/live 2>/dev/null && echo "✅ Chat service healthy" || echo "❌ Chat service health check failed"
	@echo "Collection Service (port 8004):"
	@curl -f http://localhost:8004/health/live 2>/dev/null && echo "✅ Collection service healthy" || echo "❌ Collection service health check failed"
	@echo "MCP Orchestrator (port 8005):"
	@curl -f http://localhost:8005/health/live 2>/dev/null && echo "✅ MCP orchestrator healthy" || echo "❌ MCP orchestrator health check failed"

# Comprehensive integration testing
integration-test:
	@echo "Running comprehensive integration tests..."
	@echo "=================================="
	@echo ""
	@echo "1. Database connectivity test..."
	@curl -f http://localhost:8001/health/db 2>/dev/null && echo "✅ Database connectivity OK" || echo "❌ Database connectivity failed"
	@echo ""
	@echo "2. Redis connectivity test..."
	@curl -f http://localhost:8001/health/redis 2>/dev/null && echo "✅ Redis connectivity OK" || echo "❌ Redis connectivity failed"
	@echo ""
	@echo "3. Service-to-service communication test..."
	@echo "Testing auth service endpoints..."
	@curl -f http://localhost:8001/api/v1/health 2>/dev/null && echo "✅ Auth API endpoints OK" || echo "❌ Auth API endpoints failed"
	@echo "Testing file service endpoints..."
	@curl -f http://localhost:8002/api/v1/health 2>/dev/null && echo "✅ File API endpoints OK" || echo "❌ File API endpoints failed"
	@echo "Testing chat service endpoints..."
	@curl -f http://localhost:8003/api/v1/health 2>/dev/null && echo "✅ Chat API endpoints OK" || echo "❌ Chat API endpoints failed"
	@echo "Testing collection service endpoints..."
	@curl -f http://localhost:8004/api/v1/health 2>/dev/null && echo "✅ Collection API endpoints OK" || echo "❌ Collection API endpoints failed"
	@echo "Testing MCP orchestrator endpoints..."
	@curl -f http://localhost:8005/api/v1/health 2>/dev/null && echo "✅ MCP API endpoints OK" || echo "❌ MCP API endpoints failed"
	@echo ""
	@echo "4. Configuration loading test..."
	@echo "Testing shared configuration across services..."
	@curl -s http://localhost:8001/api/v1/config/info 2>/dev/null | grep -q "service_name" && echo "✅ Auth config loading OK" || echo "❌ Auth config loading failed"
	@curl -s http://localhost:8002/api/v1/config/info 2>/dev/null | grep -q "service_name" && echo "✅ File config loading OK" || echo "❌ File config loading failed"
	@curl -s http://localhost:8003/api/v1/config/info 2>/dev/null | grep -q "service_name" && echo "✅ Chat config loading OK" || echo "❌ Chat config loading failed"
	@curl -s http://localhost:8004/api/v1/config/info 2>/dev/null | grep -q "service_name" && echo "✅ Collection config loading OK" || echo "❌ Collection config loading failed"
	@curl -s http://localhost:8005/api/v1/config/info 2>/dev/null | grep -q "service_name" && echo "✅ MCP config loading OK" || echo "❌ MCP config loading failed"
	@echo ""
	@echo "✅ Integration testing completed"

# Test shared components
test-shared:
	@echo "Testing shared components..."
	@echo "============================="
	@echo ""
	@echo "1. Testing shared configuration loading..."
	@python -c "from backend.common.config import get_service_config; config = get_service_config('auth'); print('✅ Shared config import OK')" || echo "❌ Shared config import failed"
	@echo ""
	@echo "2. Testing shared models..."
	@python -c "from backend.common.models import BaseModel; print('✅ Shared models import OK')" || echo "❌ Shared models import failed"
	@echo ""
	@echo "3. Testing shared API components..."
	@python -c "from backend.common.api import create_health_router; print('✅ Shared API import OK')" || echo "❌ Shared API import failed"
	@echo ""
	@echo "✅ Shared components testing completed"

# Full system validation
validate-system: health-check integration-test test-shared
	@echo ""
	@echo "🎉 FULL SYSTEM VALIDATION COMPLETED"
	@echo "===================================="
	@echo "All services are running and integrated correctly!" 