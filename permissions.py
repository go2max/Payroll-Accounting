from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType

# Utility to ensure perms exist on migration ready.
def ensure_permissions():
    from .models import PayrollSession
    ct = ContentType.objects.get_for_model(PayrollSession)
    Permission.objects.get_or_create(
        codename="manage", name="Can manage Payroll Accounting", content_type=ct
    )
    Permission.objects.get_or_create(
        codename="view", name="Can view Payroll Accounting", content_type=ct
    )