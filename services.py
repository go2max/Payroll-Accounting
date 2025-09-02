from decimal import Decimal

class EsiWalletAPI:
    def __init__(self, corporation_id):
        self.corporation_id = corporation_id

    def list_wallets(self):
        # TODO: integrate AA ESI client and map divisions 1..7
        return []

    def pay(self, from_division:int, to_character_id:int, amount:Decimal, reason:str="Payroll"):
        return {"tx_id": None}

def validate_percent_sum(items):
    total = sum(Decimal(i.percent) for i in items)
    return total.quantize(Decimal("0.01"))