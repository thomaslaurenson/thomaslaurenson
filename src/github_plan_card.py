import html
import logging
from pathlib import Path

from src.render_template import render_template

logger = logging.getLogger(__name__)

# Plan entries — edit to update the card. Each is a (KEYWORD, content) pair.
# KEYWORD is displayed in bold; keep the total at 8 to fit the card height.
PLAN_ENTRIES: list[tuple[str, str]] = [
    ("BUILDING", "Security utilities for Linux and OpenStack"),
    ("BUILDING", "C++ utility apps for vanilla World of Warcraft"),
    ("HACKING", "Binary differencing algorithms reversing"),
    ("HACKING", "Escaping highly restricted egress environments"),
    ("PLAYING", "Torchlight II"),
    ("READING", "The Good Guys Series by Eric Ugland"),
    ("LISTENING", "Tool - Lateralus"),
    ("EATING", "Jazzed up Shin Ramyun Black"),
]

_LINE_HEIGHT = 22
_KEYWORD_X = 0
_CONTENT_X = 110  # offset so content clears the longest keyword


def _build_plan_lines_svg(entries: list[tuple[str, str]]) -> str:
    lines = []
    for idx, (keyword, content) in enumerate(entries):
        y = idx * _LINE_HEIGHT
        delay = 200 + idx * 80
        lines.append(
            f'  <g class="stagger" style="animation-delay: {delay}ms" transform="translate(0, {y})">\n'
            f'    <text x="{_KEYWORD_X}" y="0" class="keyword">{html.escape(keyword)}</text>\n'
            f'    <text x="{_CONTENT_X}" y="0" class="content">{html.escape(content)}</text>\n'
            f"  </g>"
        )
    return "\n".join(lines)


def generate_github_plan_cards(
    templates_dir: Path,
    output_dir: Path,
) -> tuple[Path, Path]:
    logger.info("generating plan card (%d entries)", len(PLAN_ENTRIES))
    plan_lines = _build_plan_lines_svg(PLAN_ENTRIES)
    values = {"PLAN_LINES": plan_lines}

    dark_template = (templates_dir / "github_plan_card_dark.svg").read_text(encoding="utf-8")
    light_template = (templates_dir / "github_plan_card_light.svg").read_text(encoding="utf-8")

    dark_svg = render_template(dark_template, values)
    light_svg = render_template(light_template, values)

    output_dir.mkdir(parents=True, exist_ok=True)

    dark_out = output_dir / "github_plan_card_dark.svg"
    light_out = output_dir / "github_plan_card_light.svg"
    dark_out.write_text(dark_svg, encoding="utf-8")
    light_out.write_text(light_svg, encoding="utf-8")
    logger.info("wrote %s", dark_out)
    logger.info("wrote %s", light_out)

    return dark_out, light_out


def main() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    templates_dir = repo_root / "templates"
    output_dir = repo_root / "cards"

    generate_github_plan_cards(
        templates_dir=templates_dir,
        output_dir=output_dir,
    )


if __name__ == "__main__":
    main()
