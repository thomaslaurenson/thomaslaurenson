import logging
from pathlib import Path

from src.config import GH_USERNAME
from src.render_template import render_template
from src.stats import GitHubStats

logger = logging.getLogger(__name__)


def generate_github_streak_cards(
    *,
    templates_dir: Path,
    output_dir: Path,
    username: str,
) -> tuple[Path, Path]:
    logger.info("generating streak card for %s", username)
    stats = GitHubStats(username)
    streak = stats.get_streak_stats()
    first_year, first_full = stats.get_first_contribution_date()
    logger.info(
        "streak: current=%d (%s), longest=%d (%s)",
        streak["current_streak"], streak["current_range"],
        streak["longest_streak"], streak["longest_range"],
    )

    values = {
        "FIRST_CONTRIBUTION_YEAR": first_year,
        "FIRST_CONTRIBUTION_FULL": first_full,
        "CURRENT_STREAK": str(streak["current_streak"]),
        "CURRENT_STREAK_RANGE": streak["current_range"],
        "LONGEST_STREAK": str(streak["longest_streak"]),
        "LONGEST_STREAK_RANGE": streak["longest_range"],
    }

    dark_template = (templates_dir / "github_streak_card_dark.svg").read_text(encoding="utf-8")
    light_template = (templates_dir / "github_streak_card_light.svg").read_text(encoding="utf-8")

    dark_svg = render_template(dark_template, values)
    light_svg = render_template(light_template, values)

    output_dir.mkdir(parents=True, exist_ok=True)

    dark_out = output_dir / "github_streak_card_dark.svg"
    light_out = output_dir / "github_streak_card_light.svg"
    dark_out.write_text(dark_svg, encoding="utf-8")
    light_out.write_text(light_svg, encoding="utf-8")
    logger.info("wrote %s", dark_out)
    logger.info("wrote %s", light_out)

    return dark_out, light_out


def main() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    templates_dir = repo_root / "templates"
    output_dir = repo_root / "cards"

    generate_github_streak_cards(
        templates_dir=templates_dir,
        output_dir=output_dir,
        username=GH_USERNAME,
    )


if __name__ == "__main__":
    main()


