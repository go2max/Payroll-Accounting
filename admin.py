from django.contrib import admin
from .models import (
    CorpWallet, PayrollSession, Allocation, Role, RoleAssignment, RolePayout, PaymentLog, AuditLog
)

@admin.register(CorpWallet)
class CorpWalletAdmin(admin.ModelAdmin):
    list_display = ("corporation_id", "wallet_division", "wallet_name")
    list_filter = ("corporation_id",)

class AllocationInline(admin.TabularInline):
    model = Allocation
    extra = 0

class RolePayoutInline(admin.TabularInline):
    model = RolePayout
    extra = 0

@admin.register(PayrollSession)
class PayrollSessionAdmin(admin.ModelAdmin):
    list_display = ("period_label", "corporation_id", "wallet", "income_isk", "reserved_min_isk", "role_budget_isk", "created_by", "created_at")
    inlines = [AllocationInline, RolePayoutInline]

admin.site.register(Role)
admin.site.register(RoleAssignment)
admin.site.register(PaymentLog)
admin.site.register(AuditLog)