from celery import shared_task
from .models import CorpWallet
from .services import EsiWalletAPI

@shared_task
def sync_wallet_names(corporation_id:int):
    api = EsiWalletAPI(corporation_id)
    wallets = api.list_wallets()
    for w in wallets:
        obj, _ = CorpWallet.objects.update_or_create(
            corporation_id=corporation_id,
            wallet_division=w["division"],
            defaults={"wallet_name": w["name"]},
        )
    return True