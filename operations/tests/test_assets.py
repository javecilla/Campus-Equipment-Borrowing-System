"""Exercise bundle cache invalidation through real Django static-file discovery."""

from pathlib import Path
from tempfile import TemporaryDirectory

from django.core.exceptions import ImproperlyConfigured
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
