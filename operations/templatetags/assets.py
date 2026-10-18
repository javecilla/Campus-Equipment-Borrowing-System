"""Content-versioned URLs for locally built CSS and JavaScript."""

from hashlib import sha256
from pathlib import Path

from django import template
from django.contrib.staticfiles import finders
from django.core.exceptions import ImproperlyConfigured
from django.templatetags.static import static

register = template.Library()


@register.simple_tag
def compiled_asset(path: str) -> str:
    """Make browsers fetch a new bundle whenever its contents change."""
    asset_path: str | None = finders.find(path, find_all=False)
    if asset_path is None:
        raise ImproperlyConfigured(
            f"Compiled asset {path} is missing. Run npm run build before starting Django."
        )
    version: str = sha256(Path(asset_path).read_bytes()).hexdigest()[:16]
    return f"{static(path)}?v={version}"
