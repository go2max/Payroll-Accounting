from django.conf import settings
from django.db import models
from django.utils import timezone

User = settings.AUTH_USER_MODEL

class CorpWallet(models.Model):
    corporation_id = models.BigIntegerField()
    wallet_division = models.IntegerField()
    wallet_name = models.CharField(max_length=100)
    esi_wallet_id = models.CharField(max_length=64, blank=True, null=True)

    class Meta:
        unique_together = ("corporation_id", "wallet_division")

    def __str__(self):
        return f"Div {self.wallet_division} — {self.wallet_name}"

class PayrollSession(models.Model):
    corporation_id = models.BigIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    period_label = models.CharField(max_length=64, default=lambda: timezone.now().strftime("%Y-%m"))

    income_isk = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    reserved_min_isk = models.DecimalField(max_digits=20, decimal_places=2, default=0)

    wallet = models.ForeignKey(CorpWallet, on_delete=models.PROTECT, related_name="sessions")
    role_budget_isk = models.DecimalField(max_digits=20, decimal_places=2, default=0)

    note = models.TextField(blank=True, default="")
    note_locked = models.BooleanField(default=True)

    created_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name="created_payroll_sessions")

    @property
    def available_for_split(self):
        return max(self.income_isk - self.reserved_min_isk, 0)

class Allocation(models.Model):
    session = models.ForeignKey(PayrollSession, on_delete=models.CASCADE, related_name="allocations")
    name = models.CharField(max_length=64)
    percent = models.DecimalField(max_digits=6, decimal_places=2)
    notes = models.CharField(max_length=200, blank=True, default="")
    order = models.PositiveIntegerField(default=0)
    is_intake_only = models.BooleanField(default=False)

    class Meta:
        ordering = ["order", "id"]

    @property
    def amount_isk(self):
        return (self.session.available_for_split * (self.percent / 100)) if self.session else 0

class Role(models.Model):
    corporation_id = models.BigIntegerField()
    name = models.CharField(max_length=64, unique=True)
    default_percent = models.DecimalField(max_digits=6, decimal_places=2, default=0)

    def __str__(self):
        return self.name

class RoleAssignment(models.Model):
    role = models.ForeignKey(Role, on_delete=models.CASCADE, related_name="assignments")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="payroll_roles")
    active = models.BooleanField(default=True)

    class Meta:
        unique_together = ("role", "user")

class RolePayout(models.Model):
    session = models.ForeignKey(PayrollSession, on_delete=models.CASCADE, related_name="role_payouts")
    role = models.ForeignKey(Role, on_delete=models.PROTECT)
    percent = models.DecimalField(max_digits=6, decimal_places=2)

    @property
    def amount_isk(self):
        return self.session.role_budget_isk * (self.percent / 100)

class PaymentLog(models.Model):
    session = models.ForeignKey(PayrollSession, on_delete=models.PROTECT, related_name="payments")
    user = models.ForeignKey(User, on_delete=models.PROTECT, related_name="payments_received")
    role = models.ForeignKey(Role, on_delete=models.PROTECT)
    amount_isk = models.DecimalField(max_digits=20, decimal_places=2)
    paid_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name="payments_made")
    paid_at = models.DateTimeField(auto_now_add=True)
    tx_id = models.CharField(max_length=128, blank=True, default="")

class AuditLog(models.Model):
    at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    action = models.CharField(max_length=64)
    session = models.ForeignKey(PayrollSession, on_delete=models.SET_NULL, null=True, blank=True)
    details = models.JSONField(default=dict, blank=True)