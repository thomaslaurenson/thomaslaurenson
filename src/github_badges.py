import logging
import re
from pathlib import Path

from src.render_template import render_template

logger = logging.getLogger(__name__)

REPO_ROOT = Path(__file__).resolve().parents[1]
ICONS_DIR = REPO_ROOT / "icons"

BADGES = [
    {
        "label": "website",
        "value": "thomaslaurenson.com",
        "href": "https://www.thomaslaurenson.com",
        "filename": "badge_website",
        "icon": "globe.svg",
    },
    {
        "label": "email",
        "value": "thomas@thomaslaurenson.com",
        "href": "mailto:thomas@thomaslaurenson.com",
        "filename": "badge_email",
        "icon": "mail.svg",
    },
    {
        "label": "github",
        "value": "thomaslaurenson",
        "href": "https://github.com/thomaslaurenson",
        "filename": "badge_github_personal",
        "icon": "github.svg",
    },
    {
        "label": "github",
        "value": "thegraydot",
        "href": "https://github.com/thegraydot",
        "filename": "badge_github_thegraydot",
        "icon": "github.svg",
    },
    {
        "label": "linkedin",
        "value": "thomaslaurenson",
        "href": "https://www.linkedin.com/in/thomaslaurenson/",
        "filename": "badge_linkedin",
        "icon": "linkedin.svg",
    },
    {
        "label": "work",
        "value": "uni of auckland",
        "href": "https://www.auckland.ac.nz",
        "filename": "badge_work",
        "icon": "academic-cap.svg",
    },
]

# Dark:  accent #39ff14, text-primary #c8e6c8, bg #1a1a1a
# Light: accent #2a6e2a, text-primary #1a4d1a, bg #e8e8e8
DARK_PALETTE = {
    "label_bg": "#1a7a00",
    "value_bg": "#1a1a1a",
    "label_text_color": "#ffffff",
    "value_text_color": "#c8e6c8",
}

LIGHT_PALETTE = {
    "label_bg": "#1a4d1a",
    "value_bg": "#e8e8e8",
    "label_text_color": "#ffffff",
    "value_text_color": "#1a4d1a",
}

# dot icon width + gap to label text
CHAR_WIDTH: float = 6.5
PADDING: int = 10
DOT_WIDTH: int = 14
LABEL_TEXT_X: int = DOT_WIDTH + PADDING


def _calc_section_width(text: str, *, include_dot: bool = False) -> int:
    base = int(len(text) * CHAR_WIDTH) + (PADDING * 2)
    if include_dot:
        base += DOT_WIDTH
    return base


def load_icon_paths(icon_filename: str) -> str:
    content = (ICONS_DIR / icon_filename).read_text(encoding="utf-8")
    inner = re.search(r'<svg[^>]*>(.*?)</svg>', content, re.DOTALL)
    if inner:
        return inner.group(1).strip()
    return ""


def _icon_group_attrs(icon_filename: str, icon_color: str) -> str:
    content = (ICONS_DIR / icon_filename).read_text(encoding="utf-8")
    svg_tag_match = re.search(r'<svg[^>]*>', content, re.DOTALL)
    if svg_tag_match and 'stroke-width' in svg_tag_match.group():
        # Lucide-style: stroke-based
        return (
            f'fill="none" stroke="{icon_color}" '
            f'stroke-width="2" stroke-linecap="round" stroke-linejoin="round"'
        )
    # Simple Icons style: fill-based
    return f'fill="{icon_color}" stroke="none"'


def generate_badges(
    *,
    templates_dir: Path,
    output_dir: Path,
) -> list[tuple[Path, Path]]:
    template = (templates_dir / "badge.svg").read_text(encoding="utf-8")
    output_dir.mkdir(parents=True, exist_ok=True)

    results: list[tuple[Path, Path]] = []
    logger.info("generating %d badges", len(BADGES))

    for badge in BADGES:
        label: str = badge["label"]
        value: str = badge["value"]
        filename: str = badge["filename"]
        icon: str = badge["icon"]

        label_width = _calc_section_width(label, include_dot=True)
        value_width = _calc_section_width(value)
        total_width = label_width + value_width
        value_text_x = label_width + PADDING

        icon_paths = load_icon_paths(icon)
        dark_icon_attrs = _icon_group_attrs(icon, DARK_PALETTE["label_text_color"])
        light_icon_attrs = _icon_group_attrs(icon, LIGHT_PALETTE["label_text_color"])

        base_values: dict[str, str] = {
            "label": label,
            "value": value,
            "label_width": str(label_width),
            "value_width": str(value_width),
            "total_width": str(total_width),
            "label_text_x": str(LABEL_TEXT_X),
            "value_text_x": str(value_text_x),
            "icon_paths": icon_paths,
        }

        dark_values = {**base_values, "icon_group_attrs": dark_icon_attrs, **DARK_PALETTE}
        light_values = {**base_values, "icon_group_attrs": light_icon_attrs, **LIGHT_PALETTE}

        dark_svg = render_template(template, dark_values)
        light_svg = render_template(template, light_values)

        dark_out = output_dir / f"{filename}_dark.svg"
        light_out = output_dir / f"{filename}_light.svg"
        dark_out.write_text(dark_svg, encoding="utf-8")
        light_out.write_text(light_svg, encoding="utf-8")
        logger.debug("wrote badge: %s / %s", dark_out.name, light_out.name)

        results.append((dark_out, light_out))

    logger.info("wrote %d badge pairs to %s", len(results), output_dir)
    return results


def main() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    templates_dir = repo_root / "templates"
    output_dir = repo_root / "badges"

    generate_badges(templates_dir=templates_dir, output_dir=output_dir)

if __name__ == "__main__":
    main()
