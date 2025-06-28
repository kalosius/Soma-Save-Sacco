from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings  # This is key to support custom user models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model



class CustomUser(AbstractUser):
    phone_number = models.CharField(max_length=15, unique=True)
    national_id = models.CharField(max_length=20, unique=True, null=True, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)

    GENDER_CHOICES = [
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Other', 'Other'),
    ]
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, null=True, blank=True)
    next_of_kin = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return f"{self.username} ({self.email})"




# shares model
class ShareTransaction(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='share_transactions')
    number_of_shares = models.PositiveIntegerField()
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    transaction_type = models.CharField(max_length=20, default='Purchase')
    status = models.CharField(max_length=20, default='Completed')
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.number_of_shares} shares"



User = get_user_model()
class Deposit(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    tx_ref = models.CharField(max_length=100, unique=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} deposited UGX {self.amount} - {self.status}"




# accounts model for users
class Account(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    account_number = models.CharField(max_length=20, unique=True, editable=False)
    account_type = models.CharField(max_length=50, default="Savings Account")
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)  # Default balance is 0.00
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.account_number} - {self.user.username}"


def generate_unique_account_number():
    prefix = "SACCO-0100"
    from random import randint
    from .models import Account

    while True:
        random_digits = f"{randint(10000000, 99999999)}"
        account_number = f"{prefix}{random_digits}"
        if not Account.objects.filter(account_number=account_number).exists():
            return account_number


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_account_for_user(sender, instance, created, **kwargs):
    if created:
        from .models import Account
        Account.objects.create(user=instance, account_number=generate_unique_account_number())









class LoginActivity(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='login_logs')
    ip_address = models.GenericIPAddressField()
    location = models.CharField(max_length=255, blank=True, null=True)
    device = models.CharField(max_length=255, blank=True, null=True)
    login_time = models.DateTimeField(auto_now_add=True)
    logout_time = models.DateTimeField(blank=True, null=True)  # ← Add this

    def __str__(self):
        return f"{self.user.username} logged in at {self.login_time}"
