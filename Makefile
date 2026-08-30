COMPOSE = docker compose -f compose.yaml -f compose.build.yaml -f compose.dev.yaml

.PHONY: dev down test lint lint-fix

dev: ## Start the full dev stack (backend, worker, beat, frontend) via Docker Compose
	$(COMPOSE) up -d --build

down: ## Stop the dev stack
	$(COMPOSE) down

test: ## Run backend tests
	cd backend && pytest

lint: ## Check backend and frontend linting
	ruff check backend/src
	black --check backend/src
	cd frontend && npm run lint

lint-fix: ## Auto-fix backend and frontend linting issues
	ruff check --fix backend/src
	black backend/src
	cd frontend && npx eslint --fix .
