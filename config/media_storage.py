"""Build Django storage options for explicit local or private Neon media."""

import re
from collections.abc import Mapping
from typing import NotRequired, TypedDict
from urllib.parse import urlsplit

from botocore.config import Config
from django.core.exceptions import ImproperlyConfigured

from config.environment import required_value


class StorageBackend(TypedDict):
    BACKEND: str
    OPTIONS: NotRequired[dict[str, str | bool | None | Config]]


def media_storage(values: Mapping[str, str | None]) -> StorageBackend:
    """Keep local uploads by default; selecting Neon requires every credential explicitly."""
    backend: str = values.get("MEDIA_STORAGE") or "local"
    if backend == "local":
        return {"BACKEND": "django.core.files.storage.FileSystemStorage"}
    if backend != "neon":
        raise ImproperlyConfigured("MEDIA_STORAGE must be local or neon.")
    endpoint: str = required_value(values, "AWS_ENDPOINT_URL_S3")
    try:
        parsed = urlsplit(endpoint)
    except ValueError:
        raise ImproperlyConfigured("AWS_ENDPOINT_URL_S3 has a malformed host.") from None
    if (
        parsed.scheme != "https"
        or not parsed.hostname
        or parsed.username
        or parsed.password
        or parsed.query
        or parsed.fragment
        or parsed.path not in ("", "/")
    ):
        raise ImproperlyConfigured(
            "AWS_ENDPOINT_URL_S3 must be an HTTPS origin without credentials, query or path."
        )
    bucket: str = required_value(values, "AWS_STORAGE_BUCKET_NAME")
    if re.fullmatch(r"[a-z0-9][a-z0-9-]{1,61}[a-z0-9]", bucket) is None:
        raise ImproperlyConfigured("AWS_STORAGE_BUCKET_NAME must be a valid lowercase bucket name.")
    return {
        "BACKEND": "storages.backends.s3.S3Storage",
        "OPTIONS": {
            "access_key": required_value(values, "AWS_ACCESS_KEY_ID"),
            "secret_key": required_value(values, "AWS_SECRET_ACCESS_KEY"),
            "endpoint_url": endpoint,
            "region_name": required_value(values, "AWS_REGION"),
            "bucket_name": bucket,
            "default_acl": None,
            "file_overwrite": False,
            "use_threads": False,
            "client_config": Config(
                signature_version="s3v4",
                s3={"addressing_style": "path"},
                connect_timeout=10,
                read_timeout=30,
                retries={"mode": "standard", "total_max_attempts": 3},
            ),
        },
    }
