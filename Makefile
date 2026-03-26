.PHONY: help sync lock lint lint-fix github_cards github_stats_card github_streak_card github_plan_card github_activity_card github_badges clean

help:
	@echo "Targets:"
	@echo "  sync                   Install/sync deps with uv"
	@echo "  lock                   Update uv.lock"
	@echo "  lint                   Run ruff linter"
	@echo "  lint-fix               Run ruff linter and auto-fix"
	@echo "  github_cards           Render all GitHub SVGs into ./cards/"
	@echo "  github_stats_card      Render GitHub stats SVGs into ./cards/"
	@echo "  github_streak_card     Render GitHub streak SVGs into ./cards/"
	@echo "  github_plan_card       Render GitHub plan SVGs into ./cards/"
	@echo "  github_activity_card   Render GitHub activity feed SVGs into ./cards/"
	@echo "  github_badges          Render static badge SVGs into ./badges/"
	@echo "  clean                  Remove caches"

sync:
	uv sync

lock:
	uv lock

lint:
	uv run ruff check src/

lint-fix:
	uv run ruff check --fix src/

github_cards: github_stats_card github_streak_card github_plan_card github_activity_card

github_stats_card:
	uv run python -m src.github_stats_card

github_streak_card:
	uv run python -m src.github_streak_card

github_plan_card:
	uv run python -m src.github_plan_card

github_activity_card:
	uv run python -m src.github_activity_card

github_badges:
	uv run python -m src.github_badges

clean:
	rm -rf .pytest_cache .mypy_cache __pycache__ **/__pycache__ .ruff_cache
