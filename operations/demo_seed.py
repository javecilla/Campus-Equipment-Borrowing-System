"""Realistic fictional accounts for the current clean-data demonstration stage."""

from dataclasses import dataclass

from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Q

from accounts.models import User
from accounts.services import create_admin_account, register_basic_user


@dataclass(frozen=True)
class DemoIdentity:
    username: str
    first_name: str
    last_name: str


DEMO_ADMIN = DemoIdentity("andrea.mendoza", "Andrea", "Mendoza")
DEMO_BORROWERS: tuple[DemoIdentity, ...] = (
    DemoIdentity("miguel.santos", "Miguel", "Santos"),
    DemoIdentity("sofia.reyes", "Sofia", "Reyes"),
    DemoIdentity("gabriel.cruz", "Gabriel", "Cruz"),
    DemoIdentity("isabella.garcia", "Isabella", "Garcia"),
    DemoIdentity("daniel.navarro", "Daniel", "Navarro"),
    DemoIdentity("camille.torres", "Camille", "Torres"),
    DemoIdentity("rafael.ramos", "Rafael", "Ramos"),
    DemoIdentity("alyssa.flores", "Alyssa", "Flores"),
)


@transaction.atomic
def seed_demo_data(password: str) -> tuple[User, tuple[User, ...]]:
    """Create one ADMIN and eight BASIC_USER accounts without equipment/transactions.

    All identities are fictional and use reserved example.invalid emails. Existing
    unrelated records remain intact. Refuse case-insensitive username/email
    collisions atomically instead of overwriting accounts or resetting passwords.
    """
    identities: Q = Q()
    for identity in (DEMO_ADMIN, *DEMO_BORROWERS):
        identities |= Q(username__iexact=identity.username) | Q(
            email__iexact=f"{identity.username}@example.invalid"
        )
    if User.objects.filter(identities).exists():
        raise ValidationError(
            "Demonstration account usernames or emails already exist. No records changed. "
            "Use the existing accounts or manage.py changepassword USERNAME."
        )
    admin: User = create_admin_account(
        username=DEMO_ADMIN.username,
        first_name=DEMO_ADMIN.first_name,
        last_name=DEMO_ADMIN.last_name,
        email=f"{DEMO_ADMIN.username}@example.invalid",
        raw_password=password,
    )
    borrowers: tuple[User, ...] = tuple(
        register_basic_user(
            username=identity.username,
            first_name=identity.first_name,
            last_name=identity.last_name,
            email=f"{identity.username}@example.invalid",
            contact_number="",
            raw_password=password,
        )
        for identity in DEMO_BORROWERS
    )
    return admin, borrowers
