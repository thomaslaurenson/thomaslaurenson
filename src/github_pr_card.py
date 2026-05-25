"""GitHub external PR feed card."""

import html
import logging
from datetime import datetime, timezone
from pathlib import Path

from src.config import GH_USERNAME, PR_EXCLUDE_ORGS
from src.github_client import GitHubClient
from src.render_template import render_template

logger = logging.getLogger(__name__)


def _relative_time(dt: datetime) -> str:
    """Return a short human-readable relative time string."""
    diff = datetime.now(timezone.utc) - dt
    seconds = int(diff.total_seconds())
    if seconds < 3600:
        return f"{max(1, seconds // 60)}m ago"
    elif seconds < 86400:
        return f"{seconds // 3600}h ago"
    elif seconds < 7 * 86400:
        return f"{seconds // 86400}d ago"
    elif seconds < 30 * 86400:
        return f"{seconds // (7 * 86400)}w ago"
    else:
        return f"{seconds // (30 * 86400)}mo ago"


def _status_icon(status: str) -> str:
    return {"merged": "+", "open": "o"}.get(status, "x")


def _status_class(status: str) -> str:
    return {"merged": "pr-merged", "open": "pr-open"}.get(status, "pr-closed")


def _build_pr_lines_svg(prs: list[dict]) -> str:
    """Build SVG text group snippets for each PR line."""
    if not prs:
        return (
            '  <text x="0" y="0" font-family="\'Courier New\', Courier, monospace"'
            ' font-size="12" fill="#557755">no external PRs found in recent events</text>'
        )
    line_height = 22
    lines = []
    for idx, pr in enumerate(prs):
        y = idx * line_height
        delay = 200 + idx * 80
        status = pr["status"]
        icon = _status_icon(status)
        css_class = _status_class(status)
        repo = pr["repo"]
        repo_display = repo if len(repo) <= 30 else repo[:27] + "..."
        title = pr["title"]
        title_display = title if len(title) <= 48 else title[:45] + "..."
        rel = _relative_time(pr["timestamp"])
        lines.append(
            f'  <g class="stagger" style="animation-delay: {delay}ms" transform="translate(0, {y})">\n'
            f'    <text x="0"   y="0" class="pr-icon {css_class}">{html.escape(icon)}</text>\n'
            f'    <text x="20"  y="0" class="pr-repo">{html.escape(repo_display)}</text>\n'
            f'    <text x="230" y="0" class="pr-title">{html.escape(title_display)}</text>\n'
            f'    <text x="572" y="0" class="pr-time">{html.escape(rel)}</text>\n'
            f"  </g>"
        )
    return "\n".join(lines)


def generate_github_pr_cards(
    *,
    templates_dir: Path,
    output_dir: Path,
    username: str,
) -> tuple[Path, Path]:
    client = GitHubClient()

    # Build search query: authored PRs excluding the user's own repos and all
    # configured orgs (personal secondary orgs, work orgs, etc.).
    excludes = " ".join([f"-user:{username}"] + [f"-org:{org}" for org in PR_EXCLUDE_ORGS])
    query = f"is:pr author:{username} {excludes}"

    prs: list[dict] = []
    try:
        data = client.get_rest(
            "/search/issues",
            params={"q": query, "sort": "updated", "order": "desc", "per_page": 10},
        )
        items = data.get("items", []) if isinstance(data, dict) else []
        for item in items:
            # repository_url form: https://api.github.com/repos/owner/repo
            repo = item.get("repository_url", "").removeprefix("https://api.github.com/repos/")
            pr_info = item.get("pull_request", {})
            merged_at = pr_info.get("merged_at")
            state = item.get("state", "closed")
            if merged_at:
                status = "merged"
            elif state == "open":
                status = "open"
            else:
                status = "closed"
            raw_ts = item.get("updated_at", "")
            try:
                timestamp = datetime.fromisoformat(raw_ts.replace("Z", "+00:00"))
            except (ValueError, AttributeError):
                timestamp = datetime.now(timezone.utc)
            prs.append(
                {
                    "repo": repo,
                    "title": item.get("title", ""),
                    "status": status,
                    "timestamp": timestamp,
                }
            )
    except Exception as exc:
        logger.warning("failed to fetch external PRs via search: %s", exc)

    logger.debug("found %d external PRs", len(prs))

    pr_lines = _build_pr_lines_svg(prs)
    values = {"PR_LINES": pr_lines}

    dark_template = (templates_dir / "github_pr_card_dark.svg").read_text(encoding="utf-8")
    light_template = (templates_dir / "github_pr_card_light.svg").read_text(encoding="utf-8")

    dark_svg = render_template(dark_template, values)
    light_svg = render_template(light_template, values)

    output_dir.mkdir(parents=True, exist_ok=True)

    dark_out = output_dir / "github_pr_card_dark.svg"
    light_out = output_dir / "github_pr_card_light.svg"
    dark_out.write_text(dark_svg, encoding="utf-8")
    light_out.write_text(light_svg, encoding="utf-8")

    return dark_out, light_out


def main() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    templates_dir = repo_root / "templates"
    output_dir = repo_root / "cards"

    dark_out, light_out = generate_github_pr_cards(
        templates_dir=templates_dir,
        output_dir=output_dir,
        username=GH_USERNAME,
    )


if __name__ == "__main__":
    main()
