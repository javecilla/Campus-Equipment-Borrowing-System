"""Shared settings for the local server-rendered PostgreSQL application."""

import os
from pathlib import Path
from typing import TypedDict

from config.environment import ApplicationEnvironment, read_environment


class TemplateOptions(TypedDict):
    context_processors: list[str]


class TemplateBackend(TypedDict):
    BACKEND: str
    DIRS: list[Path]
    APP_DIRS: bool
    OPTIONS: TemplateOptions


class DatabaseOptions(TypedDict):
    connect_timeout: int


class DatabaseConnection(TypedDict):
    ENGINE: str
    NAME: str
    USER: str
    PASSWORD: str
    HOST: str
    PORT: int
    OPTIONS: DatabaseOptions


BASE_DIR: Path = Path(__file__).resolve().parent.parent
environment: ApplicationEnvironment = read_environment(BASE_DIR / ".env.local", os.environ)

SECRET_KEY: str = environment.secret_key
DEBUG: bool = environment.debug
ALLOWED_HOSTS: list[str] = list(environment.allowed_hosts)
CSRF_TRUSTED_ORIGINS: list[str] = list(environment.csrf_trusted_origins)

INSTALLED_APPS: list[str] = [
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "accounts",
    "inventory",
    "borrowing",
    "operations",
]

MIDDLEWARE: list[str] = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "accounts.middleware.ActiveAccountMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF: str = "config.urls"
WSGI_APPLICATION: str = "config.wsgi.application"
ASGI_APPLICATION: str = "config.asgi.application"

TEMPLATES: list[TemplateBackend] = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

DATABASES: dict[str, DatabaseConnection] = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": environment.database_name,
        "USER": environment.database_user,
        "PASSWORD": environment.database_password,
        "HOST": environment.database_host,
        "PORT": environment.database_port,
        "OPTIONS": {"connect_timeout": 5},
    },
}

AUTH_PASSWORD_VALIDATORS: list[dict[str, str]] = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE: str = "en-us"
TIME_ZONE: str = "Asia/Manila"
USE_I18N: bool = True
USE_TZ: bool = True
DEFAULT_AUTO_FIELD: str = "django.db.models.BigAutoField"
AUTH_USER_MODEL: str = "accounts.User"
LOGIN_URL: str = "accounts:login"
STATIC_URL: str = "static/"
STATICFILES_DIRS: list[Path] = [BASE_DIR / "static"]
STATIC_ROOT: Path = BASE_DIR / "staticfiles"
SESSION_COOKIE_HTTPONLY: bool = True
SESSION_COOKIE_SAMESITE: str = "Lax"
CSRF_COOKIE_SAMESITE: str = "Lax"
X_FRAME_OPTIONS: str = "DENY"
