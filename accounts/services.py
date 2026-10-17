"""Explicit account writes used by authorized setup and later account workflows."""

from django.contrib.auth.password_validation import validate_password
from django.db import transaction

from accounts.models import Profile, User, UserRole


@transaction.atomic
def create_admin_account(
    username: str,
    first_name: str,
    last_name: str,
    email: str,
    raw_password: str,
) -> User:
    """Create one active ADMIN and Profile for the CLI-only setup command."""
    normalized_username: str = User.normalize_username(username.strip())
    normalized_email: str = User.objects.normalize_email(email.strip())
    admin: User = User(
        username=normalized_username,
        first_name=first_name.strip(),
        last_name=last_name.strip(),
        email=normalized_email,
        role=UserRole.ADMIN,
        is_active=True,
        is_staff=False,
        is_superuser=False,
    )
    validate_password(raw_password, admin)
    admin.set_password(raw_password)
    admin.full_clean()
    admin.save()
    Profile.objects.create(user=admin, contact_number="")
    return admin
