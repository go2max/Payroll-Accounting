def build_menu_items(request):
    from django.urls import reverse

    can_manage = request.user.has_perm("payroll_accounting.manage")

    return [
        {
            "name": "Payroll Accounting",
            "url": reverse("payroll_accounting:dashboard"),
            "icon": "fa-solid fa-calculator",
            "order": 80,
            "is_active": can_manage,   # controls highlighting
            "visible": can_manage,     # controls whether the item shows at all
        }
    ]
