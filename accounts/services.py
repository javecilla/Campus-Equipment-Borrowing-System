"""Explicit transactional writes for account setup and account status workflows."""

from django.contrib.auth.password_validation import validate_password
from django.db import transaction

from accounts.access import require_active_admin
from accounts.models import Profile, User, UserRole
from operations.audit import write_audit
from operations.models import AuditAction, AuditTarget


class AccountStatusConflict(Exception):
    """The requested account status is already current."""


def _lock_actor_and_basic_user(actor_id: int, target_id: int) -> tuple[User, User]:
    """Lock both accounts in stable order, then recheck actor and target authority."""
    locked_users: tuple[User, ...] = tuple(
        User.objects.select_for_update().filter(pk__in=(actor_id, target_id)).order_by("pk")
    )
    users_by_id: dict[int, User] = {user.pk: user for user in locked_users}
    try:
        actor: User = users_by_id[actor_id]
        target: User = users_by_id[target_id]
    except KeyError as error:
        raise User.DoesNotExist("The actor or target account does not exist.") from error
    require_active_admin(actor)
    if target.role != UserRole.BASIC_USER:
        raise User.DoesNotExist("The target basic-user account does not exist.")
    return actor, target


@transaction.atomic
def activate_basic_user(actor_id: int, target_id: int) -> User:
    """Activate one BASIC_USER and audit the administrator in the same transaction."""
    actor, target = _lock_actor_and_basic_user(actor_id, target_id)
    if target.is_active:
        raise AccountStatusConflict("This basic-user account is already active.")
    target.is_active = True
    target.save(update_fields=["is_active"])
    write_audit(
        actor.pk,
        AuditAction.ACCOUNT_ACTIVATED,
        AuditTarget.USER,
        target.pk,
        "Basic-user account status changed from inactive to active.",
    )
    return target


@transaction.atomic
def deactivate_basic_user(actor_id: int, target_id: int) -> User:
    """Deactivate one BASIC_USER without modifying its requests, loans, or role."""
    actor, target = _lock_actor_and_basic_user(actor_id, target_id)
    if not target.is_active:
        raise AccountStatusConflict("This basic-user account is already inactive.")
    target.is_active = False
    target.save(update_fields=["is_active"])
    write_audit(
        actor.pk,
        AuditAction.ACCOUNT_DEACTIVATED,
        AuditTarget.USER,
        target.pk,
        "Basic-user account status changed from active to inactive.",
    )
    return target


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
