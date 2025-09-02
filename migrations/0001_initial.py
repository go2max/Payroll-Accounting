from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings

class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("auth", "0012_alter_user_first_name_max_length"),
    ]

    operations = [
        migrations.CreateModel(
            name="CorpWallet",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("corporation_id", models.BigIntegerField()),
                ("wallet_division", models.IntegerField()),
                ("wallet_name", models.CharField(max_length=100)),
                ("esi_wallet_id", models.CharField(blank=True, max_length=64, null=True)),
            ],
            options={"unique_together": {("corporation_id", "wallet_division")}},
        ),
        migrations.CreateModel(
            name="PayrollSession",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("corporation_id", models.BigIntegerField()),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("period_label", models.CharField(default="", max_length=64)),
                ("income_isk", models.DecimalField(decimal_places=2, default=0, max_digits=20)),
                ("reserved_min_isk", models.DecimalField(decimal_places=2, default=0, max_digits=20)),
                ("role_budget_isk", models.DecimalField(decimal_places=2, default=0, max_digits=20)),
                ("note", models.TextField(blank=True, default="")),
                ("note_locked", models.BooleanField(default=True)),
                ("wallet", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="sessions", to="payroll_accounting.corpwallet")),
                ("created_by", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="created_payroll_sessions", to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name="Role",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("corporation_id", models.BigIntegerField()),
                ("name", models.CharField(max_length=64, unique=True)),
                ("default_percent", models.DecimalField(decimal_places=2, default=0, max_digits=6)),
            ],
        ),
        migrations.CreateModel(
            name="Allocation",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=64)),
                ("percent", models.DecimalField(decimal_places=2, max_digits=6)),
                ("notes", models.CharField(blank=True, default="", max_length=200)),
                ("order", models.PositiveIntegerField(default=0)),
                ("is_intake_only", models.BooleanField(default=False)),
                ("session", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="allocations", to="payroll_accounting.payrollsession")),
            ],
            options={"ordering": ["order", "id"]},
        ),
        migrations.CreateModel(
            name="RoleAssignment",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("active", models.BooleanField(default=True)),
                ("role", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="assignments", to="payroll_accounting.role")),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="payroll_roles", to=settings.AUTH_USER_MODEL)),
            ],
            options={"unique_together": {("role", "user")}},
        ),
        migrations.CreateModel(
            name="RolePayout",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("percent", models.DecimalField(decimal_places=2, max_digits=6)),
                ("role", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to="payroll_accounting.role")),
                ("session", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="role_payouts", to="payroll_accounting.payrollsession")),
            ],
        ),
        migrations.CreateModel(
            name="PaymentLog",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("amount_isk", models.DecimalField(decimal_places=2, max_digits=20)),
                ("paid_at", models.DateTimeField(auto_now_add=True)),
                ("tx_id", models.CharField(blank=True, default="", max_length=128)),
                ("role", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to="payroll_accounting.role")),
                ("session", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="payments", to="payroll_accounting.payrollsession")),
                ("paid_by", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="payments_made", to=settings.AUTH_USER_MODEL)),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="payments_received", to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name="AuditLog",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("at", models.DateTimeField(auto_now_add=True)),
                ("action", models.CharField(max_length=64)),
                ("details", models.JSONField(blank=True, default=dict)),
                ("session", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to="payroll_accounting.payrollsession")),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]