"""Controlled fictional accounts for local authentication verification."""

from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.db import transaction

from accounts.models import Profile, User, UserRole
from accounts.services import create_admin_account

AUTH_ADMIN_USERNAME = "auth_demo_admin"
AUTH_BASIC_USERNAME = "auth_demo_user"


@transaction.atomic
def seed_auth_accounts(admin_password: str, basic_user_password: str) -> tuple[User, User]:
    """Create both test identities atomically; reject existing names without updates."""
    existing_usernames: list[str] = list(
        User.objects.filter(username__in=[AUTH_ADMIN_USERNAME, AUTH_BASIC_USERNAME])
        .order_by("username")
        .values_list("username", flat=True)
    )
    if existing_usernames:
        raise ValidationError(
            "Authentication seed cannot create accounts because these usernames already exist: "
            f"{', '.join(existing_usernames)}. No accounts were changed. "
            "Use the existing accounts; use manage.py changepassword USERNAME if needed."
        )
    admin: User = create_admin_account(
        username=AUTH_ADMIN_USERNAME,
        first_name="Fictional",
        last_name="Administrator",
        email="auth-admin@example.invalid",
        raw_password=admin_password,
    )
    basic_user: User = User(
        username=AUTH_BASIC_USERNAME,
        first_name="Fictional",
        last_name="Borrower",
        email="auth-user@example.invalid",
        role=UserRole.BASIC_USER,
        is_active=True,
        is_staff=False,
        is_superuser=False,
    )
    validate_password(basic_user_password, basic_user)
    basic_user.set_password(basic_user_password)
    basic_user.full_clean()
    basic_user.save()
    Profile.objects.create(user=basic_user, contact_number="")
    return admin, basic_user
