"""Back up shared Neon read-only, then verify recovery in a separate local database."""

import json
import os
import subprocess
from dataclasses import asdict, dataclass
from hashlib import sha256
from pathlib import Path
from shutil import copytree
from time import perf_counter

from django.apps import apps
from django.conf import settings
from django.core.files.storage import default_storage
from django.db import connection, transaction
from django.db.backends.utils import CursorWrapper
from django.test import Client, override_settings
from psycopg import sql

from accounts.models import User, UserRole
from config.environment import read_environment, read_environment_values, required_value
from inventory.models import CatalogItem


@dataclass(frozen=True)
class TableFingerprint:
    table: str
    rows: int
    sha256: str


@dataclass(frozen=True)
class PhotoFingerprint:
    path: str
    bytes: int
    sha256: str


def fingerprint_tables(cursor: CursorWrapper) -> tuple[TableFingerprint, ...]:
    """Hash every public table's complete rows in a stable order without logging contents."""
    tables: list[str] = connection.introspection.table_names(cursor)
    results: list[TableFingerprint] = []
    for table in sorted(tables):
        cursor.execute(
            sql.SQL("SELECT to_jsonb(t)::text FROM {} t ORDER BY to_jsonb(t)::text").format(
                sql.Identifier(table)
            )
        )
        digest = sha256()
        rows: list[tuple[str]] = cursor.fetchall()
        for row in rows:
            if not isinstance(row[0], str):
                raise TypeError(f"Table {table} did not return canonical JSON text.")
            digest.update(row[0].encode("utf-8") + b"\n")
        results.append(TableFingerprint(table, len(rows), digest.hexdigest()))
    return tuple(results)


def private_environment() -> dict[str, str]:
    """Pass native-tool credentials through process environment rather than command arguments."""
    configured = read_environment(settings.BASE_DIR / ".env.local", os.environ)
    return {
        **os.environ,
        "PGHOST": configured.database_host,
        "PGPORT": str(configured.database_port),
        "PGDATABASE": configured.database_name,
        "PGUSER": configured.database_user,
        "PGPASSWORD": configured.database_password,
        "PGSSLMODE": configured.database_sslmode or "disable",
        "PGCHANNELBINDING": configured.database_channel_binding or "prefer",
    }


def backup_neon(output: Path, binaries: Path) -> None:
    """Export one consistent shared snapshot and all its referenced private photo bytes."""
    connection.ensure_connection()
    if connection.settings_dict["NAME"] != "neondb":
        raise RuntimeError(
            "Shared backup expects neondb; no backup or database mutation performed."
        )
    if not output.resolve().is_relative_to((settings.BASE_DIR / "output").resolve()):
        raise ValueError(
            "Keep sensitive recovery backups under the ignored project output directory."
        )
    output.mkdir(parents=True, exist_ok=False)
    media: Path = output / "media"
    media.mkdir()
    native: dict[str, str] = private_environment()
    values = read_environment_values(settings.BASE_DIR / ".env.local", os.environ)
    direct: str | None = values.get("DATABASE_URL_UNPOOLED")
    if direct:
        direct_config = read_environment(
            settings.BASE_DIR / ".env.local",
            {
                **os.environ,
                "DATABASE_URL": direct,
            },
        )
        native = {
            **native,
            "PGHOST": direct_config.database_host,
            "PGPORT": str(direct_config.database_port),
            "PGDATABASE": direct_config.database_name,
            "PGUSER": direct_config.database_user,
            "PGPASSWORD": direct_config.database_password,
        }
    started: float = perf_counter()
    with transaction.atomic():
        with connection.cursor() as cursor:
            cursor.execute("SET TRANSACTION ISOLATION LEVEL REPEATABLE READ, READ ONLY")
            cursor.execute("SET LOCAL TIME ZONE 'UTC'")
            cursor.execute("SELECT pg_export_snapshot(), version()")
            snapshot, version = cursor.fetchone()
            tables: tuple[TableFingerprint, ...] = fingerprint_tables(cursor)
            paths: tuple[str, ...] = tuple(
                CatalogItem.objects.exclude(photo="")
                .order_by("photo")
                .values_list("photo", flat=True)
            )
            dump_started: float = perf_counter()
            subprocess.run(
                [
                    str(binaries / "pg_dump.exe"),
                    "--format=custom",
                    "--no-owner",
                    "--no-acl",
                    "--schema=public",
                    f"--snapshot={snapshot}",
                    "--file",
                    str(output / "database.dump"),
                ],
                env=native,
                check=True,
                timeout=180,
            )
            dump_seconds: float = perf_counter() - dump_started
            photos: list[PhotoFingerprint] = []
            for name in sorted(set(paths)):
                destination: Path = (media / name).resolve()
                if not destination.is_relative_to(media.resolve()):
                    raise ValueError(f"Stored media path escapes backup directory: {name!r}.")
                destination.parent.mkdir(parents=True, exist_ok=True)
                with default_storage.open(name, "rb") as source:
                    content: bytes = source.read()
                destination.write_bytes(content)
                with default_storage.open(name, "rb") as source:
                    if sha256(source.read()).digest() != sha256(content).digest():
                        raise RuntimeError(
                            f"Photo changed during backup: {name}; retain partial backup."
                        )
                photos.append(PhotoFingerprint(name, len(content), sha256(content).hexdigest()))
    (output / "manifest.json").write_text(
        json.dumps(
            {
                "source_database": "neondb",
                "server_version": version,
                "database_dump_seconds": dump_seconds,
                "total_seconds": perf_counter() - started,
                "dump_sha256": sha256((output / "database.dump").read_bytes()).hexdigest(),
                "tables": [asdict(table) for table in tables],
                "photos": [asdict(photo) for photo in photos],
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    print(
        f"Read-only shared backup: {len(tables)} tables, {len(photos)} verified referenced photos."
    )


def restore_local(backup: Path, binaries: Path, media: Path, result: Path) -> None:
    """Restore into an empty dedicated local database; verify data and protected photo delivery."""
    connection.ensure_connection()
    if (
        connection.settings_dict["NAME"] != "campus_t24_restore"
        or connection.settings_dict["HOST"] != "127.0.0.1"
    ):
        raise RuntimeError(
            "Restore requires local 127.0.0.1/campus_t24_restore; no restore performed."
        )
    if settings.STORAGES["default"]["BACKEND"] != "django.core.files.storage.FileSystemStorage":
        raise RuntimeError("Local recovery requires MEDIA_STORAGE=local.")
    if not all(
        path.resolve().is_relative_to((settings.BASE_DIR / "output").resolve())
        for path in (backup, media, result)
    ):
        raise ValueError("Keep recovery paths under the ignored project output directory.")
    with connection.cursor() as cursor:
        if connection.introspection.table_names(cursor):
            raise RuntimeError("Restore target is not empty; never overwrite an existing dataset.")
    payload = json.loads((backup / "manifest.json").read_text(encoding="utf-8"))
    if not isinstance(payload, dict) or not isinstance(payload["dump_sha256"], str):
        raise ValueError("Recovery manifest requires dump_sha256, tables and photos.")
    for key in ("tables", "photos"):
        if not isinstance(payload[key], list):
            raise ValueError(f"Recovery manifest {key} must be a list.")
    expected_tables: list[TableFingerprint] = []
    for row in payload["tables"]:
        if (
            not isinstance(row["table"], str)
            or type(row["rows"]) is not int
            or not isinstance(row["sha256"], str)
        ):
            raise ValueError(
                "Recovery table fingerprint requires table text, integer rows and SHA-256 text."
            )
        expected_tables.append(TableFingerprint(row["table"], row["rows"], row["sha256"]))
    expected_photos: list[PhotoFingerprint] = []
    for row in payload["photos"]:
        if (
            not isinstance(row["path"], str)
            or type(row["bytes"]) is not int
            or not isinstance(row["sha256"], str)
        ):
            raise ValueError(
                "Recovery photo fingerprint requires path text, integer bytes and SHA-256 text."
            )
        expected_photos.append(PhotoFingerprint(row["path"], row["bytes"], row["sha256"]))
    dump: Path = backup / "database.dump"
    if sha256(dump.read_bytes()).hexdigest() != payload["dump_sha256"]:
        raise ValueError("Database dump SHA-256 mismatch; restore refused.")
    started: float = perf_counter()
    # A schema-inclusive dump creates public itself; this new target's empty schema must go first.
    with connection.cursor() as cursor:
        cursor.execute("DROP SCHEMA public")
    connection.close()
    subprocess.run(
        [
            str(binaries / "pg_restore.exe"),
            "--single-transaction",
            "--exit-on-error",
            "--no-owner",
            "--no-acl",
            "--dbname=campus_t24_restore",
            str(dump),
        ],
        env=private_environment(),
        check=True,
        timeout=180,
    )
    restore_seconds: float = perf_counter() - started
    connection.ensure_connection()
    with connection.cursor() as cursor:
        cursor.execute("SET TIME ZONE 'UTC'")
        actual_tables: tuple[TableFingerprint, ...] = fingerprint_tables(cursor)
    if actual_tables != tuple(expected_tables):
        raise RuntimeError(
            "Restored table counts/content hashes differ from the exported snapshot."
        )
    copytree(backup / "media", media)
    for photo in expected_photos:
        restored_path: Path = (media / photo.path).resolve()
        if not restored_path.is_relative_to(media.resolve()):
            raise ValueError(f"Recovery media path escapes target directory: {photo.path!r}.")
        content: bytes = restored_path.read_bytes()
        if len(content) != photo.bytes or sha256(content).hexdigest() != photo.sha256:
            raise RuntimeError(f"Restored photo does not match snapshot: {photo.path}.")
    checks: list[str] = []
    account_password: str = required_value(
        read_environment_values(settings.BASE_DIR / ".env.local", os.environ),
        "SEED_ACCOUNT_PASSWORD",
    )
    with override_settings(MEDIA_ROOT=media):
        admin: User = User.objects.filter(role=UserRole.ADMIN, is_active=True).earliest("pk")
        borrower: User = User.objects.filter(role=UserRole.BASIC_USER, is_active=True).earliest(
            "pk"
        )
        for user, routes in (
            (
                admin,
                (
                    "/manage/",
                    "/manage/reports/loans/",
                    "/manage/reports/overdue/",
                    "/manage/reports/loans/export/",
                ),
            ),
            (borrower, ("/portal/", "/portal/equipment/", "/portal/requests/", "/portal/loans/")),
        ):
            client: Client = Client(enforce_csrf_checks=True)
            client.get("/accounts/login/", HTTP_HOST="127.0.0.1")
            signed_in = client.post(
                "/accounts/login/",
                {
                    "username": user.username,
                    "password": account_password,
                    "csrfmiddlewaretoken": client.cookies["csrftoken"].value,
                },
                HTTP_HOST="127.0.0.1",
            )
            if signed_in.status_code != 302 or signed_in["Location"] != routes[0]:
                raise RuntimeError(
                    "Restored account login failed; supply its stored private password."
                )
            checks.append("CSRF login " + user.role)
            forbidden: str = "/portal/" if user.role == UserRole.ADMIN else "/manage/"
            if client.get(forbidden, HTTP_HOST="127.0.0.1").status_code != 403:
                raise RuntimeError(f"Restored role boundary failed: {forbidden}.")
            checks.append("role denial " + user.role)
            for route in routes:
                response = client.get(route, HTTP_HOST="127.0.0.1")
                if response.status_code != 200:
                    raise RuntimeError(
                        f"Restored role HTTP check failed: {route} => {response.status_code}."
                    )
                checks.append(route)
            for item in CatalogItem.objects.exclude(photo="").filter(
                is_archived=False, category__is_archived=False
            ):
                route = (
                    f"/manage/items/{item.pk}/photo/"
                    if user.role == UserRole.ADMIN
                    else f"/portal/equipment/{item.pk}/photo/"
                )
                response = client.get(route, HTTP_HOST="127.0.0.1")
                if response.status_code != 200:
                    raise RuntimeError(
                        f"Restored photo access failed: {route} => {response.status_code}."
                    )
                delivered: bytes = b"".join(response.streaming_content)
                response.close()
                if (
                    sha256(delivered).hexdigest()
                    != sha256((media / item.photo.name).read_bytes()).hexdigest()
                ):
                    raise RuntimeError(f"Restored photo HTTP bytes differ: item {item.pk}.")
                checks.append(route)
    result.write_text(
        json.dumps(
            {
                "database_restore_seconds": restore_seconds,
                "total_restore_and_verification_seconds": perf_counter() - started,
                "tables_verified": len(actual_tables),
                "photos_verified": len(expected_photos),
                "http_checks": checks,
                "domain_models": len(
                    [
                        model
                        for model in apps.get_models()
                        if model._meta.app_label
                        in {"accounts", "inventory", "borrowing", "operations"}
                    ]
                ),
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    print(
        f"Local restore verified: {len(actual_tables)} exact table hashes, {len(expected_photos)} photo hashes, {len(checks)} HTTP checks."
    )
