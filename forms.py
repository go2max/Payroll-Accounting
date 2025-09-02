from django import forms
from .models import PayrollSession, Allocation, RolePayout, Role, RoleAssignment

class PayrollSessionForm(forms.ModelForm):
    class Meta:
        model = PayrollSession
        fields = ["income_isk", "reserved_min_isk", "wallet", "role_budget_isk", "note", "note_locked"]
        widgets = {
            "note": forms.Textarea(attrs={"rows": 3, "class": "retro-textarea", "disabled": True}),
        }

class AllocationForm(forms.ModelForm):
    class Meta:
        model = Allocation
        fields = ["name", "percent", "notes", "order", "is_intake_only"]
        widgets = {
            "percent": forms.NumberInput(attrs={"step": "0.01", "min": 0, "max": 100}),
        }

class RolePayoutForm(forms.ModelForm):
    class Meta:
        model = RolePayout
        fields = ["role", "percent"]
        widgets = {
            "percent": forms.NumberInput(attrs={"step": "0.01", "min": 0, "max": 100}),
        }

class RoleForm(forms.ModelForm):
    class Meta:
        model = Role
        fields = ["name", "default_percent"]

class RoleAssignmentForm(forms.ModelForm):
    class Meta:
        model = RoleAssignment
        fields = ["role", "user", "active"]