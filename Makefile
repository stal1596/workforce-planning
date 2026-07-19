.DEFAULT_GOAL := help

help: ## Show available commands
	@grep -E '^[a-zA-Z_-]+:.*?## ' $(MAKEFILE_LIST)

lint: ## Check all Python code with ruff
	.venv/bin/ruff check .

format: ## Auto-format all Python code
	.venv/bin/ruff format .

test: ## Run test suites (arrives in Phase 3)
	@echo "No tests yet — pytest lands in Phase 3"