"""Catch incomplete frontend builds before protected pages are requested."""

from collections.abc import Iterable

from django.apps import AppConfig
from django.contrib.staticfiles import finders
from django.core.checks import Error

REQUIRED_COMPILED_ASSETS: tuple[str, ...] = (
    "build/app.css",
    "build/workspace-navigation.js",
    "build/dashboard-charts.js",
    "build/equipment-photo.js",
    "build/request-list.js",
    "build/borrowing-slip.js",
    "build/frontend-test.js",
)


def check_compiled_assets(app_configs: Iterable[AppConfig] | None, **kwargs: object) -> list[Error]:
    """Report missing template bundles using the same discovery as compiled_asset."""
    return [
        Error(
            f"Compiled asset {path} is missing.",
            hint="Run npm ci, then npm run build from the project root before starting Django.",
            obj=path,
            id="operations.E001",
        )
        for path in REQUIRED_COMPILED_ASSETS
        if finders.find(path, find_all=False) is None
    ]
