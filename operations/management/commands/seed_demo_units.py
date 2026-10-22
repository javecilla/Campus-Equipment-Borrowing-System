"""Create missing demonstration stock for the existing active catalog."""

from datetime import date
from typing import cast

from django.core.exceptions import PermissionDenied, ValidationError
from django.core.management.base import BaseCommand, CommandError, CommandParser

from operations.demo_units import seed_demo_units


class Command(BaseCommand):
    help = "Top up each active catalog item to a minimum total unit count; retain existing stock and photos."

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument("--admin-username", required=True)
        parser.add_argument("--quantity-per-item", type=int, required=True)
        parser.add_argument(
            "--acquired-on", required=True, help="New stock acquisition date, YYYY-MM-DD."
        )

    def handle(self, *args: str, **options: str | int | bool | None) -> None:
        try:
            acquired_on: date = date.fromisoformat(cast(str, options["acquired_on"]))
        except ValueError as error:
            raise CommandError("--acquired-on must be a valid YYYY-MM-DD date.") from error
        try:
            created: int = seed_demo_units(
                cast(str, options["admin_username"]),
                cast(int, options["quantity_per_item"]),
                acquired_on,
            )
        except ValidationError as error:
            raise CommandError("; ".join(error.messages)) from error
        except PermissionDenied as error:
            raise CommandError("Unit seeding requires an active ADMIN account.") from error
        self.stdout.write(
            self.style.SUCCESS(
                f"Created {created} physical units. Existing stock/catalog/photos retained; archived items/categories excluded."
            )
        )
