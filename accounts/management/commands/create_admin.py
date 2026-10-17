"""Create an ADMIN through an authorized local management command."""

from getpass import getpass
from secrets import compare_digest
from typing import cast

from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand, CommandError, CommandParser
from django.db import IntegrityError

from accounts.models import User
from accounts.services import create_admin_account


def required_value(option: str | None, prompt: str) -> str:
    value: str = option if option is not None else input(prompt)
    if not value.strip():
        raise CommandError(f"{prompt.strip(': ')} is required.")
    return value


class Command(BaseCommand):
    help = "Create an active ADMIN account and Profile without enabling Django admin flags."

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument("--username")
        parser.add_argument("--first-name")
        parser.add_argument("--last-name")
        parser.add_argument("--email")

    def handle(self, *args: str, **options: str | int | bool | None) -> None:
        username: str = required_value(cast(str | None, options.get("username")), "Username: ")
        first_name: str = required_value(
            cast(str | None, options.get("first_name")), "First name: "
        )
        last_name: str = required_value(cast(str | None, options.get("last_name")), "Last name: ")
        email: str = required_value(cast(str | None, options.get("email")), "Email: ")
        password: str = getpass("Password: ")
        confirmation: str = getpass("Password (again): ")
        if not compare_digest(password, confirmation):
            raise CommandError("Passwords do not match; no account was created.")
        try:
            admin: User = create_admin_account(
                username=username,
                first_name=first_name,
                last_name=last_name,
                email=email,
                raw_password=password,
            )
        except ValidationError as error:
            raise CommandError("; ".join(error.messages)) from error
        except IntegrityError as error:
            raise CommandError("The administrator account could not be created.") from error
        self.stdout.write(self.style.SUCCESS(f"Created ADMIN account '{admin.username}'."))
