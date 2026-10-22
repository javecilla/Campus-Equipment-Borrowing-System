"""Exercise bundle cache invalidation through real Django static-file discovery."""

from io import StringIO
from pathlib import Path
from shutil import copytree
from tempfile import TemporaryDirectory

from django.conf import settings
from django.core.checks import CheckMessage, Tags, run_checks
from django.core.exceptions import ImproperlyConfigured
from django.core.management import call_command
from django.core.management.base import SystemCheckError
from django.test import SimpleTestCase, override_settings

from operations.templatetags.assets import compiled_asset


class CompiledAssetTests(SimpleTestCase):
    def test_content_changes_invalidate_urls_and_missing_builds_fail_clearly(self) -> None:
        with TemporaryDirectory() as temporary:
            root: Path = Path(temporary)
            (root / "build").mkdir()
            asset: Path = root / "build" / "app.css"
            with override_settings(STATICFILES_DIRS=[root]):
                asset.write_text(".grid { display: grid; }", encoding="utf-8")
                original: str = compiled_asset("build/app.css")
                self.assertEqual(compiled_asset("build/app.css"), original)
                asset.write_text(".grid { display: grid; gap: 1rem; }", encoding="utf-8")
                self.assertNotEqual(compiled_asset("build/app.css"), original)
                with self.assertRaisesMessage(ImproperlyConfigured, "npm run build"):
                    compiled_asset("build/missing.js")

    def test_missing_dashboard_bundle_fails_registered_check_then_recovers(self) -> None:
        with TemporaryDirectory() as temporary:
            root: Path = Path(temporary)
            copytree(settings.BASE_DIR / "static" / "build", root / "build")
            charts: Path = root / "build" / "dashboard-charts.js"
            contents: bytes = charts.read_bytes()
            charts.unlink()
            with override_settings(STATICFILES_DIRS=[root]):
                with self.assertRaisesMessage(SystemCheckError, "build/dashboard-charts.js"):
                    call_command("check", tags=[Tags.staticfiles], stdout=StringIO())
                charts.write_bytes(contents)
                call_command("check", tags=[Tags.staticfiles], stdout=StringIO())
                self.assertIn("?v=", compiled_asset("build/dashboard-charts.js"))

    def test_missing_build_reports_actionable_registered_errors(self) -> None:
        with TemporaryDirectory() as temporary:
            with override_settings(STATICFILES_DIRS=[Path(temporary)]):
                errors: list[CheckMessage] = run_checks(tags=[Tags.staticfiles])
                self.assertTrue(errors)
                for error in errors:
                    self.assertEqual(error.id, "operations.E001")
                    self.assertIn("npm ci", error.hint)
                    self.assertIn("npm run build", error.hint)
