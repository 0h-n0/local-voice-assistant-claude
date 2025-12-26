# Local Voice Assistant - Development Makefile
# ============================================
# Single command to start all services for local development

.PHONY: help dev backend frontend down install check-deps clean

# Default target
.DEFAULT_GOAL := help

# Colors for output
RED := \033[0;31m
GREEN := \033[0;32m
YELLOW := \033[0;33m
BLUE := \033[0;34m
NC := \033[0m # No Color

# Ports
BACKEND_PORT := 8000
FRONTEND_PORT := 3000

#==============================================================================
# Help
#==============================================================================

help: ## Show this help message
	@echo "$(BLUE)Local Voice Assistant - Development Commands$(NC)"
	@echo ""
	@echo "$(GREEN)Usage:$(NC)"
	@echo "  make <target>"
	@echo ""
	@echo "$(GREEN)Targets:$(NC)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(YELLOW)%-15s$(NC) %s\n", $$1, $$2}'

#==============================================================================
# Dependency Checks
#==============================================================================

check-deps: ## Check if required dependencies are installed
	@echo "$(BLUE)Checking dependencies...$(NC)"
	@command -v python3 >/dev/null 2>&1 || { echo "$(RED)Error: Python 3.11+ is required$(NC)"; exit 1; }
	@command -v node >/dev/null 2>&1 || { echo "$(RED)Error: Node.js 18+ is required$(NC)"; exit 1; }
	@command -v uv >/dev/null 2>&1 || { echo "$(RED)Error: uv is required. Install from https://github.com/astral-sh/uv$(NC)"; exit 1; }
	@command -v npm >/dev/null 2>&1 || { echo "$(RED)Error: npm is required$(NC)"; exit 1; }
	@echo "$(GREEN)All dependencies are installed$(NC)"

check-env: ## Check if .env file exists
	@if [ ! -f backend/.env ]; then \
		echo "$(YELLOW)Warning: backend/.env not found$(NC)"; \
		echo "$(YELLOW)Please copy backend/.env.example to backend/.env and configure it$(NC)"; \
		echo "$(YELLOW)  cp backend/.env.example backend/.env$(NC)"; \
	fi

#==============================================================================
# Installation
#==============================================================================

install: check-deps ## Install all dependencies
	@echo "$(BLUE)Installing backend dependencies...$(NC)"
	cd backend && uv sync
	@echo "$(BLUE)Installing frontend dependencies...$(NC)"
	cd frontend && npm install
	@echo "$(GREEN)All dependencies installed$(NC)"

#==============================================================================
# Development Servers
#==============================================================================

backend: check-deps check-env ## Start backend server only (FastAPI with hot reload)
	@echo "$(BLUE)Starting backend on http://localhost:$(BACKEND_PORT)$(NC)"
	cd backend && uv run uvicorn src.main:app --reload --host 0.0.0.0 --port $(BACKEND_PORT)

frontend: check-deps ## Start frontend server only (Next.js dev server)
	@echo "$(BLUE)Starting frontend on http://localhost:$(FRONTEND_PORT)$(NC)"
	cd frontend && npm run dev

dev: check-deps check-env ## Start all services (backend + frontend) with hot reload
	@echo "$(BLUE)Starting development environment...$(NC)"
	@echo "$(GREEN)Backend:  http://localhost:$(BACKEND_PORT)$(NC)"
	@echo "$(GREEN)Frontend: http://localhost:$(FRONTEND_PORT)$(NC)"
	@echo "$(YELLOW)Press Ctrl+C to stop all services$(NC)"
	@echo ""
	@trap 'kill 0' SIGINT SIGTERM EXIT; \
	(cd backend && uv run uvicorn src.main:app --reload --host 0.0.0.0 --port $(BACKEND_PORT)) & \
	(cd frontend && npm run dev) & \
	wait

#==============================================================================
# Cleanup
#==============================================================================

down: ## Stop all running services on dev ports
	@echo "$(BLUE)Stopping services...$(NC)"
	@-lsof -ti:$(BACKEND_PORT) | xargs -r kill -9 2>/dev/null || true
	@-lsof -ti:$(FRONTEND_PORT) | xargs -r kill -9 2>/dev/null || true
	@echo "$(GREEN)All services stopped$(NC)"

clean: down ## Stop services and clean temporary files
	@echo "$(BLUE)Cleaning temporary files...$(NC)"
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".next" -exec rm -rf {} + 2>/dev/null || true
	@echo "$(GREEN)Cleanup complete$(NC)"
