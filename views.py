from decimal import Decimal
from django.contrib import messages
from django.contrib.auth.decorators import permission_required, login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.db import transaction

from .forms import PayrollSessionForm, AllocationForm, RolePayoutForm, RoleForm, RoleAssignmentForm
from .models import PayrollSession, Allocation, Role, RolePayout, RoleAssignment, PaymentLog, CorpWallet, AuditLog
from .services import validate_percent_sum

@login_required
@permission_required("payroll_accounting.manage", raise_exception=True)
@transaction.atomic
def dashboard(request, session_id=None):
    session = None
    if session_id:
        session = get_object_or_404(PayrollSession, id=session_id)

    if request.method == "POST":
        if "toggle_note_lock" in request.POST and session:
            session.note_locked = not session.note_locked
            session.save()
            AuditLog.objects.create(user=request.user, action="toggle_note_lock", session=session, details={"locked": session.note_locked})
            return redirect("payroll_accounting:dashboard", session_id=session.id)

        if "save_session" in request.POST:
            form = PayrollSessionForm(request.POST, instance=session)
            if form.is_valid():
                session = form.save()
                AuditLog.objects.create(user=request.user, action="save_session", session=session)
                messages.success(request, "Session saved.")
                return redirect("payroll_accounting:dashboard", session_id=session.id)

        if "add_allocation" in request.POST and session:
            af = AllocationForm(request.POST)
            if af.is_valid():
                alloc = af.save(commit=False)
                alloc.session = session
                alloc.save()
                AuditLog.objects.create(user=request.user, action="add_allocation", session=session, details={"allocation": alloc.name})
                return redirect("payroll_accounting:dashboard", session_id=session.id)

        if "add_rolepayout" in request.POST and session:
            rf = RolePayoutForm(request.POST)
            if rf.is_valid():
                rp = rf.save(commit=False)
                rp.session = session
                rp.save()
                AuditLog.objects.create(user=request.user, action="add_rolepayout", session=session, details={"role": rp.role.name})
                return redirect("payroll_accounting:dashboard", session_id=session.id)

        if "mark_paid" in request.POST and session:
            with transaction.atomic():
                total = Decimal(0)
                for rp in session.role_payouts.select_related("role").all():
                    amount_per_role = rp.amount_isk
                    assignments = RoleAssignment.objects.filter(role=rp.role, active=True)
                    if assignments.exists():
                        share = amount_per_role / assignments.count()
                        for ra in assignments:
                            PaymentLog.objects.create(
                                session=session,
                                user=ra.user,
                                role=rp.role,
                                amount_isk=share,
                                paid_by=request.user,
                            )
                            total += share
                AuditLog.objects.create(user=request.user, action="mark_paid", session=session, details={"total_paid": str(total)})
                messages.success(request, f"Payments logged: ISK {total:,.2f}")
            return redirect("payroll_accounting:dashboard", session_id=session.id)

    session_form = PayrollSessionForm(instance=session)
    alloc_form = AllocationForm()
    rolep_form = RolePayoutForm()

    alloc_sum = validate_percent_sum(session.allocations.all()) if session else Decimal(0)
    role_sum = validate_percent_sum(session.role_payouts.all()) if session else Decimal(0)

    return render(
        request,
        "payroll_accounting/dashboard.html",
        {
            "session": session,
            "session_form": session_form,
            "alloc_form": alloc_form,
            "rolep_form": rolep_form,
            "alloc_sum": alloc_sum,
            "role_sum": role_sum,
        },
    )

@login_required
@permission_required("payroll_accounting.manage", raise_exception=True)
def roles(request):
    if request.method == "POST":
        if "add_role" in request.POST:
            form = RoleForm(request.POST)
            if form.is_valid():
                role = form.save()
                AuditLog.objects.create(user=request.user, action="add_role", details={"role": role.name})
                return redirect("payroll_accounting:roles")
        if "add_assignment" in request.POST:
            form = RoleAssignmentForm(request.POST)
            if form.is_valid():
                ra = form.save()
                AuditLog.objects.create(user=request.user, action="add_assignment", details={"role": ra.role.name, "user": ra.user_id})
                return redirect("payroll_accounting:roles")
    return render(request, "payroll_accounting/roles.html", {
        "roles": Role.objects.all(),
        "assignments": RoleAssignment.objects.select_related("role", "user").all(),
        "role_form": RoleForm(),
        "assign_form": RoleAssignmentForm(),
    })