"""Shared authentication identity; account workflows belong to their owners."""

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models


class UserRole(models.TextChoices):
    BASIC_USER = "BASIC_USER", "Basic user"
    ADMIN = "ADMIN", "Admin"


class User(AbstractUser):
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    email = models.EmailField(max_length=254)
    role = models.CharField(max_length=10, choices=UserRole.choices, default=UserRole.BASIC_USER)

    REQUIRED_FIELDS: list[str] = ["first_name", "last_name", "email"]

    class Meta:
        constraints: list[models.BaseConstraint] = [
            models.CheckConstraint(
                condition=models.Q(role__in=UserRole.values), name="user_valid_role"
            ),
        ]


class Profile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile"
    )
    contact_number = models.CharField(max_length=30, blank=True)
