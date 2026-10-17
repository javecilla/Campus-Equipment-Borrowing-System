"""Create one fictional account per role for authentication testing."""

import os

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured, ValidationError
from django.core.management.base import BaseCommand, CommandError

from accounts.models import User
from accounts.seeding import seed_auth_accounts
from config.environment import read_environment_values, required_value


class Command(BaseCommand):
    help = "Seed one fictional ADMIN and BASIC_USER using private SEED_ACCOUNT_PASSWORD."

    def handle(self, *args: str, **options: str | int | bool | None) -> None:
        try:
            values: dict[str, str | None] = read_environment_values(
                settings.BASE_DIR / ".env.local", os.environ
            )
            password: str = required_value(values, "SEED_ACCOUNT_PASSWORD")
        except ImproperlyConfigured as error:
            raise CommandError(str(error)) from error
        try:
            admin: User
            basic_user: User
            admin, basic_user = seed_auth_accounts(password, password)
        except ValidationError as error:
            raise CommandError("; ".join(error.messages)) from error
        self.stdout.write(
            self.style.SUCCESS(
                f"Created ADMIN '{admin.username}' and BASIC_USER '{basic_user.username}' "
                "with Profiles. Sign in using your private SEED_ACCOUNT_PASSWORD."
            )
        )
