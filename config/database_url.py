"""Validate PostgreSQL URLs using the installed psycopg connection parser."""

from dataclasses import dataclass
from urllib.parse import urlsplit

from django.core.exceptions import ImproperlyConfigured
from psycopg import ProgrammingError
from psycopg.conninfo import conninfo_to_dict


@dataclass(frozen=True)
class DatabaseURL:
    name: str
    user: str
    password: str
    host: str
    port: int
    sslmode: str
    channel_binding: str


def parse_database_url(value: str) -> DatabaseURL:
    """Require an explicit TLS PostgreSQL connection, without echoing credentials."""
    try:
        scheme: str = urlsplit(value).scheme
    except ValueError:
        raise ImproperlyConfigured("DATABASE_URL has a malformed host.") from None
    if scheme not in ("postgres", "postgresql"):
        raise ImproperlyConfigured("DATABASE_URL must use postgres:// or postgresql://.")
    try:
        fields: dict[str, str] = conninfo_to_dict(value)
    except ProgrammingError:
        raise ImproperlyConfigured(
            "DATABASE_URL is malformed; check the copied Neon connection string."
        ) from None
    for key in ("dbname", "user", "password", "host"):
        if not fields.get(key, "").strip():
            raise ImproperlyConfigured(f"DATABASE_URL requires a nonblank {key}.")
    port: str = fields.get("port", "5432")
    if not port.isascii() or not port.isdigit() or not 1 <= int(port) <= 65535:
        raise ImproperlyConfigured("DATABASE_URL port must be an integer from 1 to 65535.")
    sslmode: str = fields.get("sslmode", "")
    if sslmode not in ("require", "verify-ca", "verify-full"):
        raise ImproperlyConfigured(
            "DATABASE_URL must specify sslmode=require, verify-ca or verify-full."
        )
    channel_binding: str = fields.get("channel_binding", "prefer")
    if channel_binding not in ("disable", "prefer", "require"):
        raise ImproperlyConfigured(
            "DATABASE_URL channel_binding must be disable, prefer or require."
        )
    unsupported: set[str] = set(fields) - {
        "dbname",
        "user",
        "password",
        "host",
        "port",
        "sslmode",
        "channel_binding",
    }
    if unsupported:
        raise ImproperlyConfigured(
            "DATABASE_URL contains unsupported connection parameters: "
            + ", ".join(sorted(unsupported))
        )
    return DatabaseURL(
        fields["dbname"],
        fields["user"],
        fields["password"],
        fields["host"],
        int(port),
        sslmode,
        channel_binding,
    )
