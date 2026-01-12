from pathlib import Path
from math import tau

from src.config import GH_USERNAME
from src.render_template import render_template
from src.stats import GitHubStats, calculate_rank


def generate_github_stats_cards(
    *,
    templates_dir: Path,
    output_dir: Path,
    username: str,
) -> tuple[Path, Path]:
    stats = GitHubStats(username)

    display_name = stats.get_display_name()
    total_stars = stats.get_total_stars()
    commits_last_year = stats.get_commits_last_year()
    commits_all_time = stats.get_commits_all_time()
    total_prs = stats.get_total_pull_requests_created()
    total_issues = stats.get_total_issues_created()
    repos_contributed_last_year = stats.get_repos_contributed_last_year()
    followers = stats.get_followers_count()
    reviews = stats.get_total_reviews_created()

    level, percentile = calculate_rank(
        all_commits=True,
        commits=commits_all_time,
        prs=total_prs,
        issues=total_issues,
        reviews=reviews,
        stars=total_stars,
        followers=followers,
    )

    # Circle progress shows 100 - percentile; dashoffset is proportional to percentile
    circumference = tau * 40  # radius 40
    rank_dashoffset = circumference * (percentile / 100)

    values: dict[str, str] = {
        "DISPLAY_NAME": display_name,
        "RANK": level,
        "RANK_DASHOFFSET": f"{rank_dashoffset:.3f}",
        "TOTAL_STARS": str(total_stars),
        "COMMITS_LAST_YEAR": str(commits_last_year),
        "TOTAL_PRS": str(total_prs),
        "TOTAL_ISSUES": str(total_issues),
        "REPOS_CONTRIBUTED_LAST_YEAR": str(repos_contributed_last_year),
    }

    dark_template = (templates_dir / "github_stats_card_dark.svg").read_text(encoding="utf-8")
    light_template = (templates_dir / "github_stats_card_light.svg").read_text(encoding="utf-8")

    dark_svg = render_template(dark_template, values)
    light_svg = render_template(light_template, values)

    output_dir.mkdir(parents=True, exist_ok=True)

    dark_out = output_dir / "github_stats_card_dark.svg"
    light_out = output_dir / "github_stats_card_light.svg"
    dark_out.write_text(dark_svg, encoding="utf-8")
    light_out.write_text(light_svg, encoding="utf-8")

    return dark_out, light_out


def main() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    templates_dir = repo_root / "templates"
    output_dir = repo_root / "cards"

    dark_out, light_out = generate_github_stats_cards(
        templates_dir=templates_dir,
        output_dir=output_dir,
        username=GH_USERNAME,
    )

    print(f"Wrote {dark_out}")
    print(f"Wrote {light_out}")


if __name__ == "__main__":
    main()
