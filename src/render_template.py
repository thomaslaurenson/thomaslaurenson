"""Simple ``{{PLACEHOLDER}}`` template renderer for SVG files.

Usage::

    from src.render_template import render_template

    svg = render_template(template_str, {"NAME": "octocat"})
"""


def render_template(template: str, values: dict[str, str]) -> str:
    """Replace ``{{KEY}}`` placeholders in *template* with values from *values*.

    :param template: SVG template string containing ``{{KEY}}`` placeholders.
    :param values: Mapping of placeholder key to replacement string.
    :return: Rendered template with all matching placeholders substituted.
    """
    rendered = template
    for key, value in values.items():
        rendered = rendered.replace(f"{{{{{key}}}}}", value)
    return rendered
