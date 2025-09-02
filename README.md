# Payroll Accounting (Alliance Auth app)

ESI-powered corp wallet selection, allocation calculator, role payouts, audit logs, and position management.

## Install
1. Copy `payroll_accounting/` into your AA project and add to `INSTALLED_APPS`.
2. `python manage.py migrate`
3. Grant `payroll_accounting.manage` to your management group.
4. Implement `EsiWalletAPI.list_wallets()` using AA's ESI client.