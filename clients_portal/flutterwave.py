import uuid
import requests
from django.conf import settings

def initiate_momo_payment(amount, phone, email, name):
    url = f"{settings.FLW_BASE_URL}/charges?type=mobile_money_uganda"
    headers = {
        "Authorization": f"Bearer {settings.FLW_SECRET_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "tx_ref": str(uuid.uuid4()),
        "amount": str(amount),
        "currency": "UGX",
        "email": email,
        "phone_number": phone,
        "fullname": name,  # This is the key Flutterwave expects, not 'name'
        "redirect_url": "https://somasave.com/payment/callback/",
        # "redirect_url": "http://localhost:8000/payment/callback/",
        "customizations": {
            "title": "SomaSave Payments",
            "description": "Loan Repayment"
        }
    }

    print("📦 FINAL Payload to Flutterwave:")
    print(data)

    response = requests.post(url, headers=headers, json=data)
    return response.json()
