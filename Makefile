SHELL := /bin/bash

.PHONY: help
help: ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) \
		| awk 'BEGIN {FS = ":.*?## "}; {printf "  %-22s %s\n", $$1, $$2}'

# DEPS

.PHONY: sync
sync: ## Install/sync deps with uv
	uv sync

.PHONY: lock
lock: ## Update uv.lock
	uv lock

# LINT

.PHONY: lint
lint: ## Run ruff linter
	uv run ruff check src/

.PHONY: lint_fix
lint_fix: ## Run ruff linter and auto-fix
	uv run ruff check --fix src/

# TASKS

.PHONY: github_cards
github_cards: github_stats_card github_streak_card github_plan_card github_activity_card ## Render all GitHub SVGs into ./cards/

.PHONY: github_stats_card
github_stats_card: ## Render GitHub stats SVGs into ./cards/
	uv run python -m src.github_stats_card

.PHONY: github_streak_card
github_streak_card: ## Render GitHub streak SVGs into ./cards/
	uv run python -m src.github_streak_card

.PHONY: github_plan_card
github_plan_card: ## Render GitHub plan SVGs into ./cards/
	uv run python -m src.github_plan_card

.PHONY: github_activity_card
github_activity_card: ## Render GitHub activity feed SVGs into ./cards/
	uv run python -m src.github_activity_card

.PHONY: github_badges
github_badges: ## Render static badge SVGs into ./badges/
	uv run python -m src.github_badges

# CLEANUP

.PHONY: clean
clean: ## Remove caches
	rm -rf .pytest_cache .mypy_cache __pycache__ **/__pycache__ .ruff_cache
