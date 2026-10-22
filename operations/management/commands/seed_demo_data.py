"""Create realistic fictional demonstration accounts using private credentials."""

import os

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured, ValidationError
from django.core.management.base import BaseCommand, CommandError

from config.environment import read_environment_values, required_value
from operations.demo_seed import seed_demo_data


class Command(BaseCommand):
    help = "Create one admin and eight fictional borrowers using private SEED_ACCOUNT_PASSWORD."

    def handle(self, *args: str, **options: str | int | bool | None) -> None:
        try:
            values: dict[str, str | None] = read_environment_values(
                settings.BASE_DIR / ".env.local", os.environ
            )
            password: str = required_value(values, "SEED_ACCOUNT_PASSWORD")
            seed_demo_data(password)
        except ImproperlyConfigured as error:
            raise CommandError(str(error)) from error
        except ValidationError as error:
            raise CommandError("; ".join(error.messages)) from error
        self.stdout.write(
            self.style.SUCCESS(
                "Created 1 ADMIN and 8 BASIC_USER accounts with Profiles. "
                "Sign in using first.last usernames and your private SEED_ACCOUNT_PASSWORD. "
                "Equipment, maintenance, and borrowing transactions were left unchanged."
            )
        )
