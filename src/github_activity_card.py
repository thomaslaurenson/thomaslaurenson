import html
import logging
from datetime import datetime, timezone
from pathlib import Path

from src.config import GH_USERNAME
from src.github_client import GitHubClient
from src.render_template import render_template

logger = logging.getLogger(__name__)


def _relative_time(dt: datetime) -> str:
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


def _fetch_commit_message(client: GitHubClient, repo_name: str, sha: str) -> str:
    try:
        data = client.get_rest(f"/repos/{repo_name}/commits/{sha}")
        if isinstance(data, dict):
            msg = data.get("commit", {}).get("message", "")
            return msg.split("\n")[0][:70]
    except Exception:
        pass
    return ""


def _fetch_push_events(client: GitHubClient, path: str) -> list[dict]:
    entries: list[dict] = []
    try:
        events = client.get_rest(path, params={"per_page": 100})
    except Exception as exc:
        logger.warning("failed to fetch events from %s: %s", path, exc)
        return entries

    if not isinstance(events, list):
        logger.warning("unexpected response from %s: %s", path, type(events))
        return entries

    for event in events:
        if event.get("type") != "PushEvent":
            continue
        payload = event.get("payload", {})
        repo_name = event.get("repo", {}).get("name", "")
        if not repo_name:
            continue
        # New API format: commits stripped, only head SHA available
        head_sha = payload.get("head", "")
        # Old API format (fallback): commits list present
        commits = payload.get("commits", [])
        if commits:
            msg = commits[0].get("message", "").split("\n")[0][:70]
        else:
            msg = None  # resolve later via commit API
        try:
            created_at = datetime.fromisoformat(
                event["created_at"].replace("Z", "+00:00")
            )
        except (KeyError, ValueError):
            continue
        entries.append({
            "repo": repo_name,
            "message": msg,
            "head_sha": head_sha,
            "timestamp": created_at,
        })

    logger.debug("fetched %d push events from %s", len(entries), path)
    return entries


def _build_log_lines_svg(entries: list[dict]) -> str:
    if not entries:
        return (
            '  <text x="0" y="0" font-family="\'Courier New\', Courier, monospace"'
            ' font-size="12" fill="#557755">no recent push activity found</text>'
        )
    line_height = 22
    lines = []
    for idx, entry in enumerate(entries):
        y = idx * line_height
        delay = 200 + idx * 80
        rel = _relative_time(entry["timestamp"])
        repo = entry["repo"]
        repo_display = repo if len(repo) <= 41 else repo[:38] + "..."
        msg = entry["message"]
        msg_display = msg if len(msg) <= 42 else msg[:39] + "..."
        lines.append(
            f'  <g class="stagger" style="animation-delay: {delay}ms" transform="translate(0, {y})">\n'
            f'    <text x="0"   y="0" class="log-time">[{html.escape(rel)}]</text>\n'
            f'    <text x="78"  y="0" class="log-repo">{html.escape(repo_display)}</text>\n'
            f'    <text x="357" y="0" class="log-msg">{html.escape(msg_display)}</text>\n'
            f"  </g>"
        )
    return "\n".join(lines)


def generate_github_activity_cards(
    *,
    templates_dir: Path,
    output_dir: Path,
    username: str,
) -> tuple[Path, Path]:
    logger.info("generating activity card for %s", username)
    client = GitHubClient()

    entries: list[dict] = _fetch_push_events(client, f"/users/{username}/events")

    # Sort most-recent first
    entries.sort(key=lambda x: x["timestamp"], reverse=True)

    # Apply max-2-per-repo cap, then take top 8
    repo_counts: dict[str, int] = {}
    filtered: list[dict] = []
    for entry in entries:
        repo = entry["repo"]
        if repo_counts.get(repo, 0) < 2:
            filtered.append(entry)
            repo_counts[repo] = repo_counts.get(repo, 0) + 1
        if len(filtered) >= 8:
            break

    # Resolve commit messages for entries that need them (new API format)
    for entry in filtered:
        if entry["message"] is None and entry.get("head_sha"):
            entry["message"] = _fetch_commit_message(client, entry["repo"], entry["head_sha"])
        if not entry["message"]:
            entry["message"] = "(no message)"

    logger.info("activity card: %d entries after filtering", len(filtered))
    log_lines = _build_log_lines_svg(filtered)
    values = {"LOG_LINES": log_lines}

    dark_template = (templates_dir / "github_activity_card_dark.svg").read_text(encoding="utf-8")
    light_template = (templates_dir / "github_activity_card_light.svg").read_text(encoding="utf-8")

    dark_svg = render_template(dark_template, values)
    light_svg = render_template(light_template, values)

    output_dir.mkdir(parents=True, exist_ok=True)

    dark_out = output_dir / "github_activity_card_dark.svg"
    light_out = output_dir / "github_activity_card_light.svg"
    dark_out.write_text(dark_svg, encoding="utf-8")
    light_out.write_text(light_svg, encoding="utf-8")
    logger.info("wrote %s", dark_out)
    logger.info("wrote %s", light_out)

    return dark_out, light_out


def main() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    templates_dir = repo_root / "templates"
    output_dir = repo_root / "cards"

    generate_github_activity_cards(
        templates_dir=templates_dir,
        output_dir=output_dir,
        username=GH_USERNAME,
    )


if __name__ == "__main__":
    main()
