# payroll_accounting/defaults.py
from django.utils import timezone


def default_period_label():
    """Default period label for PayrollSession (e.g., '2025-09')."""
    return timezone.now().strftime("%Y-%m")


def default_notes():
    """Default notes for text fields."""
    return ""


def default_tx_id():
    """Default transaction ID."""
    return ""
