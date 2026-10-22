"""Import the fixed August-October 2026 demonstration history."""

from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from operations.demo_transactions import seed_demo_transactions


class Command(BaseCommand):
    help = "Import 30 fictional requests and 20 loans dated August-October 22, 2026, using existing equipment."

    def handle(self, *args: str, **options: str | int | bool | None) -> None:
        try:
            seed_demo_transactions(timezone.localdate())
        except ValidationError as error:
            raise CommandError("; ".join(error.messages)) from error
        self.stdout.write(
            self.style.SUCCESS(
                "Imported 30 requests and 20 loans: August 3, September 4, October 13. "
                "Existing equipment, accounts and photos retained."
            )
        )
