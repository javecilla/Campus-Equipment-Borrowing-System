"""Delete borrowing history in the configured local database."""

from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand, CommandError

from operations.demo_cleanup import clear_borrowing_data


class Command(BaseCommand):
    help = "DESTRUCTIVE: delete ALL requests, reservations, loans, returns and their audits; preserve stock, maintenance, accounts and catalog/photos. Stop the server first."

    def handle(self, *args: str, **options: str | int | bool | None) -> None:
        try:
            clear_borrowing_data()
        except ValidationError as error:
            raise CommandError("; ".join(error.messages)) from error
        self.stdout.write(
            self.style.SUCCESS(
                "All borrowing history deleted. Reserved/Issued stock is Available; maintenance retained with source-return links detached. Other stock states, catalog/photos, accounts and settings retained."
            )
        )
