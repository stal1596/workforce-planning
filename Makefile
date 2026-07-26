.DEFAULT_GOAL := help

help: ## Show available commands
	@grep -E '^[a-zA-Z_-]+:.*?## ' $(MAKEFILE_LIST)

lint: ## Check all Python code with ruff
	.venv/bin/ruff check .

format: ## Auto-format all Python code
	.venv/bin/ruff format .

test: ## Run the backend test suite
	.venv/bin/pytest backend/tests -v

up: ## Start the whole system
	docker compose up -d --build

down: ## Stop the whole system
	docker compose down

logs: ## Tail logs from every service
	docker compose logs -f