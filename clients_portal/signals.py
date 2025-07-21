# clients_portal/signals.py

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from django.contrib.auth import get_user_model
from .models import Account, Deposit
from random import randint

User = get_user_model()

from .utils import generate_unique_account_number

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_account_for_user(sender, instance, created, **kwargs):
    if created and not Account.objects.filter(user=instance).exists():
        Account.objects.create(
            user=instance,
            account_number=generate_unique_account_number()
        )
        
@receiver(post_save, sender=Deposit)
def update_account_balance_on_deposit(sender, instance, created, **kwargs):
    if created and instance.status == "successful":
        try:
            account = Account.objects.get(user=instance.user)
            account.balance += instance.amount
            account.save()
            print(f"✅ Account balance updated: UGX {account.balance}")
        except Account.DoesNotExist:
            print(f"❌ Account does not exist for user {instance.user}")
