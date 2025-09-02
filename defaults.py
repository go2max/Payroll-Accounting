from django.utils import timezone


def default_period_label():
    """
    Returns the default period label for PayrollSession.
    Example: '2025-09'
    """
    return timezone.now().strftime("%Y-%m")


def default_notes():
    """
    Default text for notes fields.
    """
    return ""


def default_tx_id():
    """
    Default value for transaction ID fields.
    """
    return ""
