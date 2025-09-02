from decimal import Decimal
from django.contrib import messages
from django.contrib.auth.decorators import permission_required, login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.db import transaction
from django.conf import settings

from .forms import (
    PayrollSessionForm,
    AllocationForm,
    RolePayoutForm,
    RoleForm,
    RoleAssignmentForm,
    PayrollSettingsForm,
)
from .models import (
    PayrollSession,
    Allocation,
    Role,
    RolePayout,
    RoleAssignment,
    PaymentLog,
    CorpWallet,
    AuditLog,
)
from .services import validate_percent_sum

# --- Helper to control app visibility ---


def user_can_access(request):
    staff_only = getattr(settings, "PAYROLL_STAFF_ONLY", True)
    return request.user.is_staff or not staff_only

# --- Dashboard / main payroll page ---


@login_required
@permission_required("payroll_accounting.manage", raise_exception=True)
@transaction.atomic
def dashboard(request, session_id=None):
    if not user_can_access(request):
        return redirect("home")

    session = get_object_or_404(
        PayrollSession, id=session_id) if session_id else None

    if request.method == "POST":
        # Toggle note lock
        if "toggle_note_lock" in request.POST and session:
            session.note_locked = not session.note_locked
            session.save()
            AuditLog.objects.create(
                user=request.user,
                action="toggle_note_lock",
                session=session,
                details={"locked": session.note_locked},
            )
            return redirect("payroll_accounting:dashboard", session_id=session.id)

        # Save session
        if "save_session" in request.POST:
            form = PayrollSessionForm(request.POST, instance=session)
            if form.is_valid():
                session = form.save()
                AuditLog.objects.create(
                    user=request.user, action="save_session", session=session)
                messages.success(request, "Session saved.")
                return redirect("payroll_accounting:dashboard", session_id=session.id)

        # Add allocation
        if "add_allocation" in request.POST and session:
            form = AllocationForm(request.POST)
            if form.is_valid():
                alloc = form.save(commit=False)
                alloc.session = session
                alloc.save()
                AuditLog.objects.create(
                    user=request.user, action="add_allocation", session=session, details={"allocation": alloc.name}
                )
                return redirect("payroll_accounting:dashboard", session_id=session.id)

        # Add role payout
        if "add_rolepayout" in request.POST and session:
            form = RolePayoutForm(request.POST)
            if form.is_valid():
                rp = form.save(commit=False)
                rp.session = session
                rp.save()
                AuditLog.objects.create(
                    user=request.user, action="add_rolepayout", session=session, details={"role": rp.role.name}
                )
                return redirect("payroll_accounting:dashboard", session_id=session.id)

        # Mark paid
        if "mark_paid" in request.POST and session:
            total_paid = Decimal(0)
            with transaction.atomic():
                for rp in session.role_payouts.select_related("role").all():
                    amount = rp.amount_isk
                    assignments = RoleAssignment.objects.filter(
                        role=rp.role, active=True)
                    if assignments.exists():
                        share = amount / assignments.count()
                        for ra in assignments:
                            PaymentLog.objects.create(
                                session=session,
                                user=ra.user,
                                role=rp.role,
                                amount_isk=share,
                                paid_by=request.user,
                            )
                            total_paid += share
            AuditLog.objects.create(user=request.user, action="mark_paid", session=session, details={
                                    "total_paid": str(total_paid)})
            messages.success(
                request, f"Payments logged: ISK {total_paid:,.2f}")
            return redirect("payroll_accounting:dashboard", session_id=session.id)

    context = {
        "session": session,
        "session_form": PayrollSessionForm(instance=session),
        "alloc_form": AllocationForm(),
        "rolep_form": RolePayoutForm(),
        "alloc_sum": validate_percent_sum(session.allocations.all()) if session else Decimal(0),
        "role_sum": validate_percent_sum(session.role_payouts.all()) if session else Decimal(0),
    }

    return render(request, "payroll_accounting/dashboard.html", context)

# --- Roles & assignments ---


@login_required
@permission_required("payroll_accounting.manage", raise_exception=True)
def roles(request):
    if not user_can_access(request):
        return redirect("home")

    if request.method == "POST":
        if "add_role" in request.POST:
            form = RoleForm(request.POST)
            if form.is_valid():
                role = form.save()
                AuditLog.objects.create(
                    user=request.user, action="add_role", details={"role": role.name})
                return redirect("payroll_accounting:roles")

        if "add_assignment" in request.POST:
            form = RoleAssignmentForm(request.POST)
            if form.is_valid():
                ra = form.save()
                AuditLog.objects.create(
                    user=request.user,
                    action="add_assignment",
                    details={"role": ra.role.name, "user": ra.user_id},
                )
                return redirect("payroll_accounting:roles")

    return render(
        request,
        "payroll_accounting/roles.html",
        {
            "roles": Role.objects.all(),
            "assignments": RoleAssignment.objects.select_related("role", "user").all(),
            "role_form": RoleForm(),
            "assign_form": RoleAssignmentForm(),
        },
    )

# --- Payroll app settings page ---


@login_required
@permission_required("payroll_accounting.manage", raise_exception=True)
def settings_view(request):
    if request.method == "POST":
        form = PayrollSettingsForm(request.POST)
        if form.is_valid():
            staff_only = form.cleaned_data["staff_only"]
            # Save to Django settings (runtime only)
            settings.PAYROLL_STAFF_ONLY = staff_only
            messages.success(
                request, f"Payroll staff-only setting updated to {staff_only}")
            return redirect("payroll_accounting:settings")
    else:
        form = PayrollSettingsForm(
            initial={"staff_only": getattr(settings, "PAYROLL_STAFF_ONLY", True)})

    return render(request, "payroll_accounting/settings.html", {"form": form})
