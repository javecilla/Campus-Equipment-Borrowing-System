"""Parse private configuration without mutating the process environment."""

import re
from collections.abc import Mapping
from dataclasses import dataclass
from ipaddress import IPv6Address
from pathlib import Path
from urllib.parse import SplitResult, urlsplit

from django.core.exceptions import ImproperlyConfigured
from dotenv.parser import Binding, parse_stream


@dataclass(frozen=True)
class ApplicationEnvironment:
    secret_key: str
    debug: bool
    allowed_hosts: tuple[str, ...]
    csrf_trusted_origins: tuple[str, ...]
    database_name: str
    database_user: str
    database_password: str
    database_host: str
    database_port: int


def required_value(values: Mapping[str, str | None], key: str) -> str:
    value: str | None = values.get(key)
    if value is None or not value.strip():
        raise ImproperlyConfigured(
            f"{key} is required; set a nonblank value in .env.local or the process environment."
        )
    return value


def comma_separated_values(value: str, key: str) -> tuple[str, ...]:
    entries: tuple[str, ...] = tuple(entry.strip() for entry in value.split(","))
    if not all(entries):
        raise ImproperlyConfigured(f"{key} must contain nonempty comma-separated entries.")
    return entries


def validate_host(host: str, key: str) -> None:
    if host == "*":
        return
    if host.startswith("[") and host.endswith("]"):
        try:
            IPv6Address(host[1:-1])
        except ValueError as error:
            raise ImproperlyConfigured(f"{key} contains an invalid IPv6 host.") from error
        return
    domain: str = host.removeprefix(".")
    if (
        len(domain) > 253
        or re.fullmatch(
            r"[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?"
            r"(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*",
            domain,
        )
        is None
    ):
        raise ImproperlyConfigured(
            f"{key} contains an invalid host; use a hostname or IP address without a scheme, port, or path."
        )


def validate_origin(origin: str) -> None:
    key: str = "DJANGO_CSRF_TRUSTED_ORIGINS"
    try:
        parsed: SplitResult = urlsplit(origin)
        port: int | None = parsed.port
    except ValueError as error:
        raise ImproperlyConfigured(f"{key} contains an invalid URL or port.") from error
    if (
        parsed.scheme not in {"http", "https"}
        or not parsed.hostname
        or parsed.username is not None
        or parsed.password is not None
        or parsed.path
        or parsed.query
        or parsed.fragment
        or any(character.isspace() for character in origin)
        or (port is not None and port < 1)
        or origin.endswith(":")
    ):
        raise ImproperlyConfigured(
            f"{key} entries must be http(s) origins with an optional port and no credentials, path, query, or fragment."
        )
    host: str = parsed.hostname.removeprefix("*.")
    if host == "*" or host.startswith("."):
        raise ImproperlyConfigured(
            f"{key} must use a concrete domain; a wildcard is allowed only as a leading '*.'."
        )
    validate_host(f"[{host}]" if ":" in host else host, key)


def read_environment(path: Path, process_environment: Mapping[str, str]) -> ApplicationEnvironment:
    """Require .env.local; explicit process values override its literal values."""
    if not path.is_file():
        raise ImproperlyConfigured(
            f"Private configuration file is missing: {path}. Copy .env.example and fill its required values."
        )
    with path.open(encoding="utf-8") as stream:
        bindings: tuple[Binding, ...] = tuple(parse_stream(stream))
    for binding in bindings:
        if binding.error:
            raise ImproperlyConfigured(
                f"Invalid .env.local syntax at line {binding.original.line}; check quotes and KEY=value formatting."
            )
    keys: tuple[str, ...] = tuple(binding.key for binding in bindings if binding.key is not None)
    if len(keys) != len(set(keys)):
        raise ImproperlyConfigured(
            "Duplicate keys in .env.local; keep exactly one definition per key."
        )
    file_values: dict[str, str | None] = {
        binding.key: binding.value for binding in bindings if binding.key is not None
    }
    values: dict[str, str | None] = {**file_values, **process_environment}
    secret_key: str = required_value(values, "DJANGO_SECRET_KEY")
    if (
        len(secret_key) < 50
        or len(set(secret_key)) < 5
        or secret_key.startswith("django-insecure-")
    ):
        raise ImproperlyConfigured(
            "DJANGO_SECRET_KEY must be a unique random secret of at least 50 characters; generate it as described in DEV.md."
        )
    debug_value: str = required_value(values, "DJANGO_DEBUG")
    if debug_value not in {"True", "False"}:
        raise ImproperlyConfigured("DJANGO_DEBUG must be exactly True or False.")
    port_value: str = required_value(values, "DB_PORT")
    if re.fullmatch(r"[0-9]{1,5}", port_value) is None or not 1 <= int(port_value) <= 65535:
        raise ImproperlyConfigured("DB_PORT must be an integer from 1 to 65535.")
    hosts: tuple[str, ...] = comma_separated_values(
        required_value(values, "DJANGO_ALLOWED_HOSTS"), "DJANGO_ALLOWED_HOSTS"
    )
    for host in hosts:
        validate_host(host, "DJANGO_ALLOWED_HOSTS")
    origins: tuple[str, ...] = comma_separated_values(
        required_value(values, "DJANGO_CSRF_TRUSTED_ORIGINS"), "DJANGO_CSRF_TRUSTED_ORIGINS"
    )
    for origin in origins:
        validate_origin(origin)
    database_host: str = required_value(values, "DB_HOST")
    validate_host(f"[{database_host}]" if ":" in database_host else database_host, "DB_HOST")
    if database_host == "*" or database_host.startswith("."):
        raise ImproperlyConfigured(
            "DB_HOST must identify one database server; wildcards are invalid."
        )
    return ApplicationEnvironment(
        secret_key=secret_key,
        debug=debug_value == "True",
        allowed_hosts=hosts,
        csrf_trusted_origins=origins,
        database_name=required_value(values, "DB_NAME"),
        database_user=required_value(values, "DB_USER"),
        database_password=required_value(values, "DB_PASSWORD"),
        database_host=database_host,
        database_port=int(port_value),
    )
