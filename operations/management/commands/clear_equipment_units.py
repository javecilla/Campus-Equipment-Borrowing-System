"""Delete physical stock and maintenance in the configured local database."""

from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand, CommandError

from operations.demo_cleanup import clear_equipment_units


class Command(BaseCommand):
    help = "DESTRUCTIVE: delete ALL physical units, maintenance and their audits; preserve catalog/photos, accounts and settings. Requires empty borrowing history. Stop the server first."

    def handle(self, *args: str, **options: str | int | bool | None) -> None:
        try:
            clear_equipment_units()
        except ValidationError as error:
            raise CommandError("; ".join(error.messages)) from error
        self.stdout.write(
            self.style.SUCCESS(
                "All physical units and maintenance deleted. Categories, catalog/photo references, accounts and settings retained."
            )
        )
