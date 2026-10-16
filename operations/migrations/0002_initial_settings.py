"""Initialize the required settings singleton and its system audit together."""

from django.apps.registry import Apps
from django.db import migrations
from django.db.backends.base.schema import BaseDatabaseSchemaEditor
from django.utils import timezone


def initialize_settings(apps: Apps, schema_editor: BaseDatabaseSchemaEditor) -> None:
    setting_model = apps.get_model("operations", "SystemSetting")
    audit_model = apps.get_model("operations", "AuditLog")
    database_alias: str = schema_editor.connection.alias
    occurred_at = timezone.now()
    setting_model.objects.using(database_alias).create(
        id=1,
        max_loan_days=7,
        max_quantity_per_item=3,
        updated_at=occurred_at,
        updated_by_id=None,
    )
    audit_model.objects.using(database_alias).create(
        actor_id=None,
        actor_kind="SYSTEM",
        action="SETTINGS_INITIALIZED",
        occurred_at=occurred_at,
        target_model="operations.SystemSetting",
        target_id=1,
        summary="Initial limits: maximum loan duration 7 calendar days; maximum quantity 3 units per item.",
    )


class Migration(migrations.Migration):
    dependencies = [("operations", "0001_initial")]
    operations = [migrations.RunPython(initialize_settings)]
