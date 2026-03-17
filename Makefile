.DEFAULT_GOAL := help
.PHONY: help install dev test test-cov lint format format-check typecheck check audit clean build docker-build docker-run docs-serve docs-build bootstrap new

unexport VIRTUAL_ENV

help: ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}'

install: ## Install production dependencies
	uv sync

dev: ## Set up full development environment
	uv sync --extra dev
	uv run pre-commit install

test: ## Run tests
	uv run pytest

test-cov: ## Run tests with coverage report
	uv run pytest --cov --cov-report=term-missing --cov-report=html

lint: ## Check code for linting violations
	uv run ruff check .

format: ## Auto-format code
	uv run ruff format .
	uv run ruff check --fix .

format-check: ## Verify code formatting (no changes)
	uv run ruff format --check .

typecheck: ## Run static type analysis
	uv run mypy src/

check: lint format-check typecheck test ## Run all quality gates

audit: ## Scan dependencies for known vulnerabilities
	uv run pip-audit

clean: ## Remove generated files
	rm -rf __pycache__ .pytest_cache .mypy_cache .ruff_cache
	rm -rf htmlcov .coverage coverage.xml
	rm -rf dist build *.egg-info
	rm -rf site
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true

build: ## Build distribution packages
	uv build

docker-build: ## Build Docker image
	docker build -t myproject:latest .

docker-run: ## Run Docker container
	docker run --rm myproject:latest

docs-serve: ## Serve documentation locally with live reload
	uv run mkdocs serve

docs-build: ## Build static documentation site
	uv run mkdocs build

bootstrap: ## Rename project (one-time after cloning scaffold)
	python scripts/bootstrap.py

new: ## Create new project from scaffold: make new PROJECT=my_app [PARENT=..]
ifndef PROJECT
	$(error PROJECT is required. Usage: make new PROJECT=my_app)
endif
	$(eval PARENT ?= ..)
	$(eval PYNAME := $(subst -,_,$(PROJECT)))
	$(eval DEST := $(PARENT)/$(PROJECT))
	@if [ -d "$(DEST)" ]; then echo "Error: $(DEST) already exists"; exit 1; fi
	git clone git@github.com:grggls/python-scaffold.git "$(DEST)"
	cd "$(DEST)" && rm -rf .git
	cd "$(DEST)" && python scripts/bootstrap.py "$(PYNAME)"
	cd "$(DEST)" && git init && git add . && git commit -m "Initial commit from python-scaffold"
	cd "$(DEST)" && gh repo create grggls/$(PROJECT) --private --source=. --remote=origin --push
	@echo "Configuring branch protection for main..."
	gh api repos/grggls/$(PROJECT)/branches/main/protection \
		--method PUT \
		--field 'required_pull_request_reviews[required_approving_review_count]=0' \
		--field 'required_pull_request_reviews[dismiss_stale_reviews]=true' \
		--field 'enforce_admins=true' \
		--field 'required_linear_history=true' \
		--field 'allow_force_pushes=false' \
		--field 'allow_deletions=false' \
		--field 'restrictions=null' \
		--field 'required_status_checks=null' \
		> /dev/null
	@echo "Branch protection enabled on main."
	@echo ""
	@echo "Project created: $(DEST)"
	@echo "GitHub repo:     https://github.com/grggls/$(PROJECT)"
	@echo ""
	@echo "Next steps:"
	@echo "  cd $(DEST)"
	@echo "  make dev"
	@echo "  make check"
