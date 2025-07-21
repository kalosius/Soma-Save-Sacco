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
            print(f"Deposit ID: {instance.id}, User: {instance.user.username} ({instance.user.id}), Amount: {instance.amount}")
            account = Account.objects.get(user=instance.user)
            print(f"Before update: Account {account.account_number} balance = {account.balance}")
            account.balance += instance.amount
            account.save()
            print(f"After update: Account {account.account_number} balance = {account.balance}")
        except Account.DoesNotExist:
            print(f"❌ Account does not exist for user {instance.user}")
