.PHONY: help sync lock run github_stats_card github_languages_card github_streak_card clean

help:
	@echo "Targets:"
	@echo "  sync				Install/sync deps with uv"
	@echo "  lock				Update uv.lock"
	@echo "  github_stats_card	Render GitHub stats SVGs into ./cards/"
	@echo "  github_languages_card	Render GitHub languages SVGs into ./cards/"
	@echo "  github_streak_card	Render GitHub streak SVGs into ./cards/"
	@echo "  clean				Remove caches"

sync:
	uv sync

lock:
	uv lock

github_stats_card:
	uv run python -m src.github_stats_card

github_languages_card:
	uv run python -m src.github_languages_card

github_streak_card:
	uv run python -m src.github_streak_card

clean:
	rm -rf .pytest_cache .mypy_cache __pycache__ **/__pycache__ .ruff_cache
