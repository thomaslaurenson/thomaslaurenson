SHELL := /bin/bash
TAG ?= $(shell git describe --tags --abbrev=0 2>/dev/null)

.PHONY: help
help: ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) \
		| awk 'BEGIN {FS = ":.*?## "}; {printf "  %-30s %s\n", $$1, $$2}'

# DEPS
.PHONY: sync
sync: ## Install/sync deps with uv
	uv sync

.PHONY: lock
lock: ## Update uv.lock
	uv lock

# LINT
.PHONY: fmt
fmt: ## Format code with ruff
	uv run ruff format src/

.PHONY: fmt_check
fmt_check: ## Check formatting with ruff (no changes)
	uv run ruff format --check src/

.PHONY: lint
lint: ## Run ruff linter
	uv run ruff check src/

.PHONY: fix
fix: ## Run ruff linter and auto-fix
	uv run ruff check --fix src/

# TASKS
.PHONY: github_cards
github_cards: github_stats_card github_streak_card github_pr_card github_plan_card github_activity_card ## Render all GitHub SVGs into ./cards/

.PHONY: github_stats_card
github_stats_card: ## Render GitHub stats SVGs into ./cards/
	uv run python -m src.github_stats_card

.PHONY: github_streak_card
github_streak_card: ## Render GitHub streak SVGs into ./cards/
	uv run python -m src.github_streak_card

.PHONY: github_pr_card
github_pr_card: ## Render GitHub external PR SVGs into ./cards/
	uv run python -m src.github_pr_card

.PHONY: github_plan_card
github_plan_card: ## Render GitHub plan SVGs into ./cards/
	uv run python -m src.github_plan_card

.PHONY: github_activity_card
github_activity_card: ## Render GitHub activity feed SVGs into ./cards/
	uv run python -m src.github_activity_card

.PHONY: github_badges
github_badges: ## Render static badge SVGs into ./badges/
	uv run python -m src.github_badges

# GET
.PHONY: get_python_project_version
get_python_project_version: ## Print the project version from pyproject.toml
	@grep '^version = ' pyproject.toml | grep -oE '[0-9]+\.[0-9]+\.[0-9]+'

.PHONY: get_python_required_version
get_python_required_version: ## Print the required Python version from pyproject.toml
	@grep 'requires-python' pyproject.toml | grep -oE '[0-9]+\.[0-9]+'

# CLEANUP
.PHONY: ci
ci: lint fmt_check ## Run all CI checks locally

.PHONY: clean
clean: ## Remove caches
	rm -rf .pytest_cache .mypy_cache __pycache__ **/__pycache__ .ruff_cache
