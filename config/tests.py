"""Bootstrap checks without migrations or database access."""

import secrets
from pathlib import Path
from tempfile import TemporaryDirectory

from django.core.exceptions import ImproperlyConfigured
from django.test import SimpleTestCase

from config.environment import ApplicationEnvironment, read_environment


def configuration_values() -> dict[str, str]:
    return {
        "DJANGO_SECRET_KEY": secrets.token_urlsafe(64),
        "DJANGO_DEBUG": "False",
        "DJANGO_ALLOWED_HOSTS": "localhost, 127.0.0.1, [::1], .example.com",
        "DJANGO_CSRF_TRUSTED_ORIGINS": "http://localhost:8000, https://*.example.com",
        "DB_NAME": "bootstrap_test",
        "DB_USER": "bootstrap_test",
        "DB_PASSWORD": "literal-${NOT_INTERPOLATED}-#-password",
        "DB_HOST": "127.0.0.1",
        "DB_PORT": "5432",
    }


def write_configuration(path: Path, values: dict[str, str]) -> None:
    content: str = "\n".join(f"{key}='{value}'" for key, value in values.items())
    path.write_text(content, encoding="utf-8")


class EnvironmentTests(SimpleTestCase):
    def test_private_file_and_explicit_process_override(self) -> None:
        values: dict[str, str] = configuration_values()
        process_values: dict[str, str] = {"DJANGO_DEBUG": "True", "UNRELATED_KEY": "ignored"}
        with TemporaryDirectory() as directory:
            path: Path = Path(directory) / ".env.local"
            write_configuration(path, values)
            environment: ApplicationEnvironment = read_environment(path, process_values)
        self.assertTrue(environment.debug)
        self.assertEqual(environment.database_port, 5432)
        self.assertEqual(environment.database_password, values["DB_PASSWORD"])
        self.assertEqual(
            environment.allowed_hosts, ("localhost", "127.0.0.1", "[::1]", ".example.com")
        )
        self.assertEqual(process_values, {"DJANGO_DEBUG": "True", "UNRELATED_KEY": "ignored"})

    def test_missing_private_file_fails_with_setup_instruction(self) -> None:
        with TemporaryDirectory() as directory:
            with self.assertRaisesMessage(ImproperlyConfigured, "Copy .env.example"):
                read_environment(Path(directory) / ".env.local", {})

    def test_invalid_file_syntax_and_duplicate_keys_fail_explicitly(self) -> None:
        with TemporaryDirectory() as directory:
            path: Path = Path(directory) / ".env.local"
            for suffix, message in (
                ("\nBROKEN='unterminated\n", "Invalid .env.local syntax at line"),
                ("\nDB_PORT='5433'\n", "Duplicate keys in .env.local"),
            ):
                with self.subTest(message=message):
                    write_configuration(path, configuration_values())
                    path.write_text(path.read_text(encoding="utf-8") + suffix, encoding="utf-8")
                    with self.assertRaisesMessage(ImproperlyConfigured, message):
                        read_environment(path, {})

    def test_each_required_value_rejects_missing_and_blank_input(self) -> None:
        values: dict[str, str] = configuration_values()
        with TemporaryDirectory() as directory:
            path: Path = Path(directory) / ".env.local"
            for key in values:
                with self.subTest(key=key, case="missing"):
                    write_configuration(
                        path, {name: value for name, value in values.items() if name != key}
                    )
                    with self.assertRaisesMessage(ImproperlyConfigured, key):
                        read_environment(path, {})
                with self.subTest(key=key, case="blank override"):
                    write_configuration(path, values)
                    with self.assertRaisesMessage(ImproperlyConfigured, key):
                        read_environment(path, {key: " "})

    def test_invalid_configuration_fails_without_exposing_values(self) -> None:
        invalid_values: dict[str, tuple[str, ...]] = {
            "DJANGO_SECRET_KEY": ("short-private-secret", "a" * 60),
            "DJANGO_DEBUG": ("true", "0", "False "),
            "DB_PORT": ("0", "65536", "5432.0", "not-a-port", "9" * 5000),
            "DJANGO_ALLOWED_HOSTS": (
                "localhost,",
                "http://localhost",
                "localhost:8000",
                "bad host",
            ),
            "DJANGO_CSRF_TRUSTED_ORIGINS": (
                "https://*",
                "https://.example.com",
                "http://loc\nalhost",
                "localhost:8000",
                "ftp://localhost",
                "https://localhost/path",
                "https://user:private@localhost",
                "https://localhost:65536",
                "https://localhost:0",
                "http://[invalid]",
                "https://localhost?query",
                "https://localhost#fragment",
            ),
            "DB_HOST": ("*", ".example.com", "localhost:5432", "http://localhost"),
        }
        with TemporaryDirectory() as directory:
            path: Path = Path(directory) / ".env.local"
            write_configuration(path, configuration_values())
            for key, candidates in invalid_values.items():
                for value in candidates:
                    with self.subTest(key=key, value_length=len(value)):
                        with self.assertRaises(ImproperlyConfigured) as raised:
                            read_environment(path, {key: value})
                        self.assertIn(key, str(raised.exception))
                        self.assertNotIn(value, str(raised.exception))


class BootstrapTests(SimpleTestCase):
    def test_development_and_unimplemented_routes_are_unavailable_without_debug(self) -> None:
        with self.settings(DEBUG=False, ALLOWED_HOSTS=["testserver"]):
            for path in ("/", "/admin/", "/manage/", "/portal/"):
                with self.subTest(path=path):
                    self.assertEqual(self.client.get(path).status_code, 404)

    def test_wsgi_and_asgi_entry_points_boot(self) -> None:
        from config.asgi import application as asgi_application
        from config.wsgi import application as wsgi_application

        self.assertTrue(callable(wsgi_application))
        self.assertTrue(callable(asgi_application))
