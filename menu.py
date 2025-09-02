def build_menu_items(request):
    from django.urls import reverse
    return [
        {
            "name": "Payroll Accounting",
            "url": reverse("payroll_accounting:dashboard"),
            "icon": "fa-solid fa-calculator",
            "order": 80,
            "is_active": request.user.has_perm("payroll_accounting.manage"),
        }
    ]