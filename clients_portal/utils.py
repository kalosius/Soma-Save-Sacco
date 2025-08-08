# clients_portal/utils.py

from random import randint

def generate_unique_account_number():
    from .models import Account  # import here to avoid circular import
    prefix = "SACCO-0100"
    while True:
        random_digits = f"{randint(10000000, 99999999)}"
        account_number = f"{prefix}{random_digits}"
        if not Account.objects.filter(account_number=account_number).exists():
            return account_number
        