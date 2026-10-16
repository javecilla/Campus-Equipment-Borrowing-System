"""Read the required operational singleton without inventing missing settings."""

from django.core.exceptions import ImproperlyConfigured

from operations.models import SystemSetting
from operations.validation import LoanLimits, validate_loan_limits


def get_loan_limits() -> LoanLimits:
    """A single SELECT captures both limits consistently for a new request."""
    try:
        setting: SystemSetting = SystemSetting.objects.get(pk=1)
    except SystemSetting.DoesNotExist as error:
        raise ImproperlyConfigured(
            "SystemSetting row 1 is missing. Apply the settings initialization migration on a fresh database or restore the missing row from a verified backup; request submission cannot continue."
        ) from error
    return validate_loan_limits(setting.max_loan_days, setting.max_quantity_per_item)
