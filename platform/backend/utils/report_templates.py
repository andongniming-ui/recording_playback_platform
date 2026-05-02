"""Small file-based template renderer for generated reports."""
from pathlib import Path
from string import Template


TEMPLATE_DIR = Path(__file__).resolve().parent.parent / "templates"


def render_template(template_name: str, context: dict[str, object]) -> str:
    template_path = TEMPLATE_DIR / template_name
    template = Template(template_path.read_text(encoding="utf-8"))
    return template.safe_substitute({key: "" if value is None else str(value) for key, value in context.items()})
