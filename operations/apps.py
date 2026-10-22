"""Register project checks through Django's application lifecycle."""

from django.apps import AppConfig
from django.core.checks import Tags, register


class OperationsConfig(AppConfig):
    name: str = "operations"

    def ready(self) -> None:
        from operations.checks import check_compiled_assets

        register(check_compiled_assets, Tags.staticfiles)
