from math import tau
from pathlib import Path
from typing import Iterable

from src.config import GH_USERNAME
from src.stats import GitHubStats
from src.render_template import render_template


PALETTE = [
    "#2EA043",  # github green
    "#1F6FEB",  # indigo
    "#A371F7",  # purple
    "#3FB950",  # mint green
    "#F778BA",  # pink accent
    "#54AEFF",  # sky blue
]


def _build_lang_items(langs: list[dict[str, float]]) -> str:
    """Build the stacked language rows SVG snippet."""
    row_spacing = 26
    rows = []
    for idx, lang in enumerate(langs):
        dy = idx * row_spacing
        color = lang["color"]
        name = lang["language"]
        pct = f'{lang["percentage"]:.2f}%'
        rows.append(
            f"""<g transform="translate(0, {dy})">
    <g class="stagger" style="animation-delay: {450 + idx*120}ms">
      <circle cx="5" cy="6" r="5" fill="{color}" />
      <text data-testid="lang-name" x="15" y="10" class='lang-name'>
        {name} ({pct})
      </text>
    </g>
  </g>"""
        )
    return "\n".join(rows)


def _build_lang_donuts(langs: list[dict[str, float]]) -> str:
    """Build donut arcs using circles with stroke-dasharray."""
    cx = 116.6667
    cy = 116.6667
    r = 56.6667
    circumference = tau * r
    donuts = []
    offset_pct = 0.0
    for idx, lang in enumerate(langs):
        pct = lang["percentage"]
        color = lang["color"]
        dash = circumference * pct / 100.0
        # Rotate each segment so they stack around the circle
        angle = 360.0 * offset_pct / 100.0 - 90.0  # start at top
        donuts.append(
            f"""<g class="stagger" style="animation-delay: {600 + idx*100}ms">
        <circle
          data-testid="lang-donut"
          size="{pct:.2f}"
          cx="{cx}"
          cy="{cy}"
          r="{r}"
          stroke="{color}"
          fill="none"
          stroke-width="12"
          stroke-dasharray="{dash:.3f} {circumference:.3f}"
          stroke-dashoffset="0"
          transform="rotate({angle:.3f} {cx} {cy})">
        </circle>
      </g>"""
        )
        offset_pct += pct
    return "\n".join(donuts)


def _assign_colors(langs: Iterable[dict[str, float]]) -> list[dict[str, float]]:
    """Attach a color to each language using a repeating palette."""
    enriched = []
    for idx, lang in enumerate(langs):
        color = PALETTE[idx % len(PALETTE)]
        enriched.append({**lang, "color": color})
    return enriched


def _normalize_percentages(langs: list[dict[str, float]]) -> list[dict[str, float]]:
    total_bytes = sum(lang.get("bytes", 0) for lang in langs)
    if total_bytes <= 0:
        return langs
    normalized = []
    for lang in langs:
        pct = (lang.get("bytes", 0) / total_bytes) * 100
        normalized.append({**lang, "percentage": round(pct, 2)})
    return normalized


def generate_github_languages_cards(
    *,
    templates_dir: Path,
    output_dir: Path,
    username: str,
) -> tuple[Path, Path]:
    stats = GitHubStats(username)
    display_name = stats.get_display_name()
    top_langs = stats.get_top_languages(6)
    top_langs = _assign_colors(_normalize_percentages(top_langs))

    lang_items = _build_lang_items(top_langs)
    lang_donuts = _build_lang_donuts(top_langs)

    values = {
        "LANG_TITLE": f"{display_name}'s Top Languages",
        "LANG_DESC": f"Top 6 languages by bytes for {display_name}",
        "LANG_ITEMS": lang_items,
        "LANG_DONUTS": lang_donuts,
    }

    dark_template = (templates_dir / "github_languages_card_dark.svg").read_text(encoding="utf-8")
    light_template = (templates_dir / "github_languages_card_light.svg").read_text(encoding="utf-8")

    dark_svg = render_template(dark_template, values)
    light_svg = render_template(light_template, values)

    output_dir.mkdir(parents=True, exist_ok=True)

    dark_out = output_dir / "github_languages_card_dark.svg"
    light_out = output_dir / "github_languages_card_light.svg"
    dark_out.write_text(dark_svg, encoding="utf-8")
    light_out.write_text(light_svg, encoding="utf-8")

    return dark_out, light_out


def main() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    templates_dir = repo_root / "templates"
    output_dir = repo_root / "cards"

    dark_out, light_out = generate_github_languages_cards(
        templates_dir=templates_dir,
        output_dir=output_dir,
        username=GH_USERNAME,
    )

    print(f"Wrote {dark_out}")
    print(f"Wrote {light_out}")


if __name__ == "__main__":
    main()
