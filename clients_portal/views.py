import json
import uuid
import cloudinary
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import get_user_model, authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.hashers import make_password
from django.contrib.auth.decorators import login_required
from .models import ShareTransaction, Account, generate_unique_account_number, LoginActivity, Deposit
from django.contrib.auth.models import User
from adminapp.models import Loan, Payment, Borrower, RepaymentSchedule
from django.db.models import Sum, F, Value, CharField
from datetime import timedelta
import random, string
from django.utils import timezone
from decimal import Decimal
from datetime import datetime
from django.views.decorators.http import require_POST
from django.db.models import Q
from django.utils.dateparse import parse_date
from itertools import chain
from django.core.mail import send_mail
import requests
from django.utils.timezone import now
from user_agents import parse as parse_ua
import csv
from io import BytesIO, StringIO
from reportlab.pdfgen import canvas
from django.http import HttpResponse
from itertools import chain
from datetime import datetime
from django.conf import settings
from urllib.parse import unquote
from django.http import JsonResponse
from .flutterwave import initiate_momo_payment
from django.db import transaction
import re
from django.contrib.auth import update_session_auth_hash
from .forms import CustomPasswordChangeForm
from django.core.paginator import Paginator

from django.core.mail import EmailMultiAlternatives
from django.utils.html import strip_tags

# id verification view
import pytesseract
from PIL import Image
from django.shortcuts import render, redirect
from .forms import NationalIDVerificationForm
from .models import NationalIDVerification

# google text recognition
# from google.cloud import vision
import io



# APIS from the serializers.py
from rest_framework import viewsets
from .models import CustomUser, ShareTransaction, Deposit, Account, LoginActivity
from .serializers import UserSerializer, ShareTransactionSerializer, DepositSerializer, AccountSerializer, LoginActivitySerializer

class UserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer

class ShareTransactionViewSet(viewsets.ModelViewSet):
    queryset = ShareTransaction.objects.all()
    serializer_class = ShareTransactionSerializer

class DepositViewSet(viewsets.ModelViewSet):
    queryset = Deposit.objects.all()
    serializer_class = DepositSerializer

class AccountViewSet(viewsets.ModelViewSet):
    queryset = Account.objects.all()
    serializer_class = AccountSerializer

class LoginActivityViewSet(viewsets.ModelViewSet):
    queryset = LoginActivity.objects.all()
    serializer_class = LoginActivitySerializer



# Not working
# Initialize Vision API client once globally
# client = vision.ImageAnnotatorClient()

# def extract_and_verify(file_obj):
#     # Reset file pointer and read content
#     file_obj.seek(0)
#     content = file_obj.read()

#     image = vision.Image(content=content)
#     response = client.text_detection(image=image)

#     if response.error.message:
#         return {'status': 'Declined', 'text': '', 'error': response.error.message}

#     annotations = response.text_annotations
#     if not annotations:
#         return {'status': 'Declined', 'text': ''}

#     text = annotations[0].description.upper()

#     # Extract fields with regex
#     nin = re.search(r'[A-Z0-9]{14}', text)
#     card_number = re.search(r'\b\d{9}\b', text)
#     dob_match = re.search(r'\d{2}\.\d{2}\.\d{4}', text)
#     sex = ''
#     # More precise sex extraction
#     sex_match = re.search(r'\bSEX\s*[:\-]?\s*(M|F)\b', text)
#     if sex_match:
#         sex = sex_match.group(1)
#     else:
#         sex = 'F' if 'F' in text else ('M' if 'M' in text else '')

#     nationality = 'UGA' if 'UGA' in text else ''

#     surname_match = re.search(r'SURNAME\s*[:\-]?\s*([A-Z]+)', text)
#     given_name_match = re.search(r'GIVEN NAME[S]?\s*[:\-]?\s*([A-Z]+)', text)

#     surname = surname_match.group(1) if surname_match else ''
#     given_name = given_name_match.group(1) if given_name_match else ''
#     full_name = f"{surname} {given_name}" if surname and given_name else ''

#     dob = None
#     if dob_match:
#         try:
#             dob = datetime.strptime(dob_match.group(), '%d.%m.%Y')
#         except ValueError:
#             dob = None

#     result = {
#         'nin': nin.group() if nin else '',
#         'card_number': card_number.group() if card_number else '',
#         'dob': dob,
#         'nationality': nationality,
#         'sex': sex,
#         'full_name': full_name,
#         'status': 'Accepted' if nin and card_number and dob and full_name else 'Declined',
#         'text': text
#     }

#     return result


# def verify_id_view(request):
#     if request.method == 'POST':
#         form = NationalIDVerificationForm(request.POST, request.FILES)
#         if form.is_valid():
#             instance = form.save(commit=False)

#             front_image = request.FILES.get('front_image')
#             back_image = request.FILES.get('back_image')

#             front_result = extract_and_verify(front_image) if front_image else {'status': 'Declined', 'text': ''}
#             back_result = extract_and_verify(back_image) if back_image else {'status': 'Declined', 'text': ''}

#             # Merge front and back results
#             instance.nin = front_result.get('nin') or back_result.get('nin')
#             instance.card_number = front_result.get('card_number') or back_result.get('card_number')
#             instance.date_of_birth = front_result.get('dob') or back_result.get('dob')
#             instance.nationality = front_result.get('nationality') or back_result.get('nationality')
#             instance.sex = front_result.get('sex') or back_result.get('sex')
#             instance.full_name = front_result.get('full_name') or back_result.get('full_name')
#             instance.extracted_text_front = front_result.get('text')
#             instance.extracted_text_back = back_result.get('text')

#             instance.status = 'Accepted' if all([
#                 instance.nin, instance.card_number,
#                 instance.date_of_birth, instance.nationality,
#                 instance.sex, instance.full_name
#             ]) else 'Declined'

#             instance.save()
#             return render(request, 'auth/verify_result.html', {'obj': instance})
#     else:
#         form = NationalIDVerificationForm()
#     return render(request, 'auth/verify_form.html', {'form': form})










def startt(request):
    return render(request, 'index.html')
def momo_payment_form(request):
    return render(request, "momo_payment.html")


def momo_payment_initiate(request):
    if request.method == "POST":
        full_name = request.POST.get("name")
        email = request.POST.get("email")
        phone = request.POST.get("phone")
        amount = request.POST.get("amount")

        print("🟢 Received payment form values:")
        print(f"Name: {full_name}, Email: {email}, Phone: {phone}, Amount: {amount}")

        if not request.user.is_authenticated:
            messages.error(request, "You must be logged in to make a payment.")
            return redirect("login")

        # ✅ Include user_id in tx_ref for reliable matching during callback
        tx_ref = f"{uuid.uuid4()}_user_{request.user.id}"
        redirect_url = "https://somasave.com/payment/callback/"  # Update for production
        # redirect_url = "http://localhost:8000/payment/callback/"  # Change for production


        payload = {
            "tx_ref": tx_ref,
            "amount": str(amount),
            "currency": "UGX",
            "email": email,
            "phone_number": phone,
            "fullname": full_name,
            "redirect_url": redirect_url,
            "customizations": {
                "title": "SomaSave Payments",
                "description": "Loan Repayment",
            }
        }

        print("📦 FINAL Payload to Flutterwave:")
        print(payload)

        headers = {
            "Authorization": f"Bearer {settings.FLW_SECRET_KEY}",
            "Content-Type": "application/json"
        }

        response = requests.post(
            "https://api.flutterwave.com/v3/charges?type=mobile_money_uganda",
            json=payload,
            headers=headers
        )

        flutter_response = response.json()
        print("📤 Flutterwave response:", flutter_response)

        redirect_url = flutter_response.get("meta", {}).get("authorization", {}).get("redirect")

        if redirect_url:
            return redirect(redirect_url)
        else:
            messages.error(request, "Payment could not be initiated. Please try again.")
            return redirect("momo_payment_form")

    return redirect("momo_payment_form")

User = get_user_model()
def flutterwave_callback(request):
    raw_resp = request.GET.get("resp")
    if not raw_resp:
        return render(request, "payment_callback.html", {
            "status": "error",
            "message": "Missing payment response."
        })

    try:
        decoded = json.loads(unquote(raw_resp))
        payment_data = decoded.get("data", {})
        status = payment_data.get("status")
        tx_ref = payment_data.get("txRef")
        amount = payment_data.get("amount")

        # ✅ Extract user_id from tx_ref like: c3a3..._user_46
        user_id = None
        if tx_ref and "_user_" in tx_ref:
            try:
                user_id = int(tx_ref.split("_user_")[-1])
            except ValueError:
                pass

        if not user_id:
            return render(request, "payment_callback.html", {
                "status": "error",
                "message": "User ID not found in tx_ref."
            })

        user = User.objects.filter(id=user_id).first()
        if not user:
            return render(request, "payment_callback.html", {
                "status": "error",
                "message": "User not found."
            })

        print(f"✅ Matched user from tx_ref: {user.username} ({user.email})")

        if status == "successful":
            try:
                with transaction.atomic():
                    deposit_amount = Decimal(str(amount))
                    deposit, created = Deposit.objects.get_or_create(
                        tx_ref=tx_ref,
                        defaults={
                            "user": user,
                            "amount": deposit_amount,
                            "status": status,
                        }
                    )
                    if not created:
                        deposit.status = status
                        deposit.amount = deposit_amount
                        deposit.save()

                    print(f"💾 Deposit {'created' if created else 'updated'} for {user}")

            except Exception as e:
                print(f"❌ Error saving deposit: {e}")
                return render(request, "payment_callback.html", {
                    "status": "error",
                    "message": "Failed to save deposit"
                })

        return render(request, "payment_callback.html", {
            "status": status,
            "amount": amount,
            "tx_ref": tx_ref,
            "message": payment_data.get("chargeResponseMessage", "")
        })

    except Exception as e:
        print(f"❌ Callback parsing error: {e}")
        return render(request, "payment_callback.html", {
            "status": "error",
            "message": f"Callback error: {str(e)}"
        }) 
    
# getting the ip address
def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def get_location_from_ip(ip):
    try:
        response = requests.get(f'https://ipapi.co/{ip}/json/').json()
        city = response.get('city')
        country = response.get('country_name')
        return f"{city}, {country}" if city and country else "Unknown Location"
    except:
        return "Unknown Location"





# Transactions
@login_required(login_url='login')
def transactions(request):
    user = request.user
    search_query = request.GET.get('search', '')
    txn_type = request.GET.get('type', '')

    transactions = []

    # Deposits
    if txn_type in ['', 'deposit']:
        deposits = Deposit.objects.filter(user=user)
        if search_query:
            deposits = deposits.filter(tx_ref__icontains=search_query)
        for dep in deposits:
            transactions.append({
                'date': dep.created_at,
                'type': 'deposit',
                'description': f'Deposit Ref: {dep.tx_ref}',
                'amount': dep.amount,
                'balance_after': '—',  # If you have running balance logic
                'status': dep.status
            })

    # Share Transactions
    if txn_type in ['', 'share']:
        shares = ShareTransaction.objects.filter(user=user)
        if search_query:
            shares = shares.filter(transaction_type__icontains=search_query)
        for s in shares:
            transactions.append({
                'date': s.timestamp,
                'type': 'share',
                'description': f'{s.transaction_type} - {s.number_of_shares} shares',
                'amount': s.amount,
                'balance_after': '—',
                'status': s.status
            })

    # Payments (for loans)
    if txn_type in ['', 'loan', 'withdrawal']:
        try:
            borrower = Borrower.objects.get(user=user)
            payments = Payment.objects.filter(borrower=borrower)
            if search_query:
                payments = payments.filter(loan__loan_code__icontains=search_query)
            for p in payments:
                transactions.append({
                    'date': p.payment_date,
                    'type': 'loan',
                    'description': f'Loan Payment - Loan #{p.loan.loan_code}',
                    'amount': -p.amount,  # Payments are outgoing
                    'balance_after': '—',
                    'status': p.payment_status
                })
        except Borrower.DoesNotExist:
            pass

    # Optional: Sort by date descending
    transactions = sorted(transactions, key=lambda x: x['date'], reverse=True)

    # Pagination
    paginator = Paginator(transactions, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'main/transactions.html', {
        'transactions': page_obj.object_list,
        'page_obj': page_obj,
        'is_paginated': page_obj.has_other_pages(),
    })

# withdrawal
@login_required(login_url='login')
def withdrawal(request):
    if request.method == 'POST':
        amount = request.POST.get('amount')
        # Here you would typically handle the withdrawal logic
        messages.success(request, f'Withdrawal of {amount} processed successfully.')
        return redirect('client_dashboard')
    return render(request, 'main/withdraw.html')


# loan request
@login_required(login_url='login')
def loanrequest(request):
    user = request.user
    try:
        borrower = user.borrower_profile
    except Borrower.DoesNotExist:
        messages.error(request, "You must be registered as a borrower to request a loan.")
        return redirect('client_dashboard')

    if request.method == 'POST':
        amount = request.POST.get('amount')
        interest_rate = request.POST.get('interest_rate')

        if not amount or not interest_rate:
            messages.error(request, "All fields are required.")
            return redirect('loanrequest')

        try:
            loan = Loan.objects.create(
                borrower=borrower,
                amount=amount,
                interest_rate=interest_rate,
                loan_status='Pending',
                start_date=timezone.now(),
                due_date=timezone.now() + timedelta(days=90),
                loan_code=generate_unique_loan_code()
            )
            messages.success(request, "Loan request submitted successfully.")
            return redirect('client_dashboard')
        except Exception as e:
            messages.error(request, f"An error occurred: {e}")
            return redirect('loanrequest')

    return render(request, 'main/loanrequest.html')

def generate_unique_loan_code():
    from adminapp.models import Loan
    while True:
        code = str(random.randint(1000000, 9999999))  # 7-digit code
        if not Loan.objects.filter(loan_code=code).exists():
            return code





# statement
@login_required(login_url='login')
def statement(request):
    user = request.user
    borrower = getattr(user, 'borrower_profile', None)

    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    transaction_type = request.GET.get('transaction_type')

    # Share Transactions
    share_txns = ShareTransaction.objects.filter(user=user).values(
        'timestamp', 'transaction_type', 'amount', 'status'
    )
    share_data = [
        {
            'date': tx['timestamp'],
            'type': tx['transaction_type'].replace('_', ' ').title(),
            'reference': f"SHR-{tx['timestamp'].strftime('%Y%m%d%H%M%S')}",
            'amount': tx['amount'],
            'status': tx['status'].title()
        } for tx in share_txns
    ]

    # Loan Payments
    payments = Payment.objects.filter(borrower=borrower).select_related('loan').values(
        'id', 'payment_date', 'amount', 'payment_status', 'loan__loan_code'
    )
    payment_data = [
        {
            'date': tx['payment_date'],
            'type': "Loan Repayment",
            'reference': tx['loan__loan_code'] if tx['loan__loan_code'] else f"PAY-{tx['id']}",
            'amount': -tx['amount'],
            'status': tx['payment_status'].title()
        } for tx in payments
    ]

    # Deposits
    deposits = Deposit.objects.filter(user=user).values(
        'tx_ref', 'amount', 'status', 'created_at'
    )
    deposit_data = [
        {
            'date': tx['created_at'],
            'type': "Deposit",
            'reference': tx['tx_ref'],
            'amount': tx['amount'],
            'status': tx['status'].title()
        } for tx in deposits
    ]

    # Combine all transaction types
    transactions = sorted(
        chain(share_data, payment_data, deposit_data),
        key=lambda x: x['date'],
        reverse=True
    )

    # Filters
    if start_date:
        transactions = [tx for tx in transactions if tx['date'].date() >= datetime.strptime(start_date, "%Y-%m-%d").date()]
    if end_date:
        transactions = [tx for tx in transactions if tx['date'].date() <= datetime.strptime(end_date, "%Y-%m-%d").date()]
    if transaction_type:
        # Match type with user filter (e.g., "loan_repayment" or "deposit")
        transactions = [
            tx for tx in transactions
            if tx['type'].lower().replace(" ", "_") == transaction_type
        ]

    context = {
        'transactions': transactions,
    }
    return render(request, 'main/mystatement.html', context)



# shares
SHARE_VALUE = 6000  # Current share value in UGX
@login_required(login_url='login')
def shares(request):
    user = request.user
    transactions = ShareTransaction.objects.filter(user=user).order_by('-timestamp')

    total_shares = sum(t.number_of_shares for t in transactions)
    estimated_value = total_shares * SHARE_VALUE

    if request.method == 'POST':
        try:
            num_shares = int(request.POST.get('number_of_shares'))
            if num_shares < 1:
                raise ValueError("Must be a positive number")

            total_amount = num_shares * SHARE_VALUE
            ShareTransaction.objects.create(
                user=user,
                number_of_shares=num_shares,
                amount=total_amount
            )
            messages.success(request, f'Successfully purchased {num_shares} shares.')
            return redirect('shares')
        except ValueError:
            messages.error(request, 'Invalid number of shares.')

    context = {
        'total_shares': total_shares,
        'current_share_value': SHARE_VALUE,
        'estimated_value': estimated_value,
        'transactions': transactions
    }
    return render(request, 'main/shares.html', context)


# User loans
@login_required(login_url='login')
def user_loans(request):
    try:
        borrower = Borrower.objects.get(user=request.user)
    except Borrower.DoesNotExist:
        # Optional: redirect to borrower registration form
        # return redirect('add_borrower')

        # OR: Show a template with a message
        return render(request, 'main/user_loans.html', {
            'message': 'You have not applied for any loans yet.',
        })

    loans = Loan.objects.filter(borrower=borrower)
    active_loans = loans.filter(loan_status='Approved')
    payments = Payment.objects.filter(borrower=borrower)

    total_borrowed = loans.aggregate(Sum('amount'))['amount__sum'] or 0
    total_repaid = payments.aggregate(Sum('amount'))['amount__sum'] or 0
    outstanding_balance = total_borrowed - total_repaid

    # Prepare repayment schedules per loan
  # Flattened structure for template looping
    loan_schedule_data = []

    for loan in loans:
        loan_schedules = RepaymentSchedule.objects.filter(loan=loan).order_by('due_date')
        loan_schedule_data.append({
            'loan': loan,
            'schedules': loan_schedules
        })

    context = {
        'active_loans': active_loans,
    'loans': loans,
    'total_borrowed': total_borrowed,
    'total_repaid': total_repaid,
    'outstanding_balance': outstanding_balance,
    'loan_schedule_data': loan_schedule_data,
    }
    return render(request, 'main/user_loans.html', context)


# account
@login_required(login_url='login')
def user_account(request):
    user = request.user

    try:
        borrower = Borrower.objects.get(user=user)
    except Borrower.DoesNotExist:
        return render(request, 'main/account.html', {
            'message': 'No borrower profile found for this user.'
        })

    # Account activation logic
    if request.method == "POST" and request.POST.get("activate_account") == "1":
        if not hasattr(user, 'account'):
            Account.objects.create(
                user=user,
                account_number=generate_unique_account_number()
            )
            messages.success(request, "Account activated successfully.")
        return redirect('account')  

    # If account doesn't exist yet, show modal
    if not hasattr(user, 'account'):
        return render(request, 'main/account.html', {
            'show_activation_modal': True,
        })

    account = user.account

    # Financial data
    total_savings = Decimal('0')  # Replace with actual logic
    share_capital = ShareTransaction.objects.filter(user=user).aggregate(total=Sum('amount'))['total'] or 0
    outstanding_loan = Loan.objects.filter(borrower=borrower, loan_status='Approved').aggregate(
        total=Sum('amount'))['total'] or 0
    dividends_earned = Decimal('0')  # Replace with logic

    transactions = []

    # Share Transactions
    for tx in ShareTransaction.objects.filter(user=user):
        transactions.append({
            'date': tx.timestamp,
            'type': 'Share Transaction',
            'description': f'{tx.transaction_type} - {tx.number_of_shares} shares',
            'amount': tx.amount,
            'status': tx.status,
        })

    # Loan Payments
    for p in Payment.objects.filter(borrower=borrower):
        transactions.append({
            'date': p.payment_date,
            'type': 'Loan Repayment',
            'description': f'Repayment for Loan #{p.loan.loan_code}',
            'amount': -p.amount,
            'status': p.payment_status,
        })

    # Deposits
    for d in Deposit.objects.filter(user=user):
        transactions.append({
            'date': d.created_at,
            'type': 'Deposit',
            'description': f'Deposit - Ref: {d.tx_ref}',
            'amount': d.amount,
            'status': d.status,
        })

    # Sort all transactions
    transactions = sorted(transactions, key=lambda x: x['date'], reverse=True)

    context = {
        'account_number': account.account_number,
        'account_type': "Savings Account",
        'member_since': borrower.date_joined.strftime('%A, %B %d, %Y'),
        'total_savings': total_savings,
        'share_capital': share_capital,
        'outstanding_loan': outstanding_loan,
        'dividends_earned': dividends_earned,
        'account_balance': account.balance,
        'recent_transactions': transactions[:5],
    }
    return render(request, 'main/account.html', context)



# userprofile
@login_required(login_url='login')
def userprofile(request):
    try:
        borrower = request.user.borrower_profile  # Uses related_name
    except Borrower.DoesNotExist:
        # Optional: Redirect or create profile
        return render(request, 'main/userprofile.html', {'message': 'You don’t have a borrower profile yet.'})

    return render(request, 'main/userprofile.html',{'borrower': borrower})


# dashboard
@login_required(login_url='login')
def client_dashboard(request): 

    # Example carousel items (can fetch from DB instead)
    carousel_items = [
        {
            'title': 'New Savings Plan!',
            'description': 'Earn up to 10% more on your deposits.',
            'image_url': '/static/images/dashboard/savings_offer.jpg',  # Replace with your image path
        },
        {
            'title': 'Exclusive Loan Offer!',
            'description': 'Low-interest loans available now.',
            'image_url': '/static/images/dashboard/loan.jpg',
        },
        {
            'title': 'Mobile App Launched!',
            'description': 'Manage your finances on the go.',
            'image_url': '/static/images/dashboard/mobile_app.jpg',
        },
    ]

    user = request.user

    # Shares data
    shares = ShareTransaction.objects.filter(user=user, status='Completed')
    total_shares = shares.aggregate(total=Sum('number_of_shares'))['total'] or 0
    total_share_value = shares.aggregate(value=Sum('amount'))['value'] or 0

    # Borrower profile
    borrower = getattr(user, 'borrower_profile', None)

    # Account info (adjust depending on your Account model)
    account = Account.objects.filter(user=user).first()
    account_number = account.account_number if account else "N/A"
    account_balance = account.balance if account else 0

    # Loan data
    loans = Loan.objects.filter(borrower=borrower) if borrower else Loan.objects.none()
    loan_requests = loans.count()
    approved_loans = loans.filter(loan_status='Approved').count()
    total_requested_amount = loans.aggregate(total=Sum('amount'))['total'] or 0
    processed_amount = loans.filter(loan_status='Approved').aggregate(total=Sum('amount'))['total'] or 0

    # Transactions (Payments) data
    payments = Payment.objects.filter(borrower=borrower) if borrower else Payment.objects.none()
    total_transactions = payments.count()
    total_transacted_amount = payments.aggregate(total=Sum('amount'))['total'] or 0

    # greeting message based on time of day
    current_hour = timezone.localtime().hour


    logs = LoginActivity.objects.filter(user=request.user).order_by('-login_time')[:10]  # latest 10


    context = {
        'carousel_items': carousel_items,
        'total_shares': total_shares,
        'total_share_value': total_share_value,
        'loan_requests': loan_requests,
        'approved_loans': approved_loans,
        'total_requested_amount': total_requested_amount,
        'processed_amount': processed_amount,
        'total_transactions': total_transactions,
        'total_transacted_amount': total_transacted_amount,
        'current_hour': current_hour,
        'account_number': account_number,
        'account_balance': account_balance,
        'logs': logs,
    }

    return render(request, 'main/client_dashboard.html', context)



# login
def login_view(request):
    if request.method == 'POST':
        identifier = request.POST.get('username').strip()
        password = request.POST.get('password')

        # Find username by email or directly
        if '@' in identifier:
            try:
                user_obj = User.objects.get(email=identifier)
                username = user_obj.username
            except User.DoesNotExist:
                username = None
        else:
            username = identifier

        # Authenticate
        user = authenticate(request, username=username, password=password) if username else None

        if user is None:
            return render(request, 'auth/login.html', {'error': 'Invalid username/email or password'})

        # ✅ Check if user is verified
        if not user.is_verified:
            # For existing users without OTP, generate one
            if not user.otp_code:
                otp = generate_otp()
                user.otp_code = otp
                user.otp_created_at = timezone.now()
                user.save()

                # send OTP email
                subject = 'Verify your SomaSave Account'
                html_content = f"""
                <p>Hello {user.first_name},</p>
                <p>Your OTP code is: <strong>{otp}</strong></p>
                <p>This code will expire in 10 minutes.</p>
                """
                text_content = strip_tags(html_content)
                email_msg = EmailMultiAlternatives(
                    subject=subject,
                    body=text_content,
                    from_email='info@somasave.com',
                    to=[user.email],
                )
                email_msg.attach_alternative(html_content, "text/html")
                email_msg.send()

            # store pending email in session for resend
            request.session['pending_email'] = user.email

            messages.info(request, 'Please verify your email to continue.')
            return redirect('verify_email')

        # login success
        login(request, user)
        messages.success(request, f'Welcome! {user.username} Login successful')
        return redirect('client_dashboard')

    return render(request, 'auth/login.html')

# register
def generate_otp(length=6):
    return ''.join(random.choices(string.digits, k=length))

User = get_user_model()
def register_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        phone_number = request.POST.get('phone_number')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        context = {
            'username': username,
            'email': email,
            'phone_number': phone_number,
            'first_name': first_name,
            'last_name': last_name,
        }

        # validations
        if password != confirm_password:
            context['error'] = 'Passwords do not match'
            return render(request, 'auth/register.html', context)

        if User.objects.filter(username=username).exists():
            context['error'] = 'Username already taken'
            return render(request, 'auth/register.html', context)

        if User.objects.filter(email=email).exists():
            context['error'] = 'Email already in use'
            return render(request, 'auth/register.html', context)

        if User.objects.filter(phone_number=phone_number).exists():
            context['error'] = 'Phone number already in use'
            return render(request, 'auth/register.html', context)

        # create user unverified
        user = User.objects.create(
            username=username,
            email=email,
            phone_number=phone_number,
            first_name=first_name,
            last_name=last_name,
            password=make_password(password),
            is_verified=False
        )

        Borrower.objects.create(user=user)

        # generate OTP
        otp = generate_otp()
        user.otp_code = otp
        user.otp_created_at = timezone.now()
        user.save()

        # store email in session for resend OTP
        request.session['pending_email'] = email

        # send OTP email
        subject = 'Verify your SomaSave Account'
        html_content = f"""
        <p>Hello {first_name},</p>
        <p>Your OTP code is: <strong>{otp}</strong></p>
        <p>This code will expire in 10 minutes.</p>
        """
        text_content = strip_tags(html_content)

        email_msg = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email='info@somasave.com',
            to=[email],
        )
        email_msg.attach_alternative(html_content, "text/html")
        email_msg.send()

        messages.info(request, 'We sent you an OTP. Please verify your email.')
        return redirect('verify_email')  # stop here (no welcome email yet!)

    return render(request, 'auth/register.html')

def verify_email(request):
    if request.method == 'POST':
        otp = request.POST.get('otp')
        try:
            user = User.objects.get(otp_code=otp, is_verified=False)

            if timezone.now() > user.otp_created_at + timedelta(minutes=10):
                messages.error(request, 'OTP expired. Please request a new one.')
                return redirect('resend_otp')

            user.is_verified = True
            user.otp_code = None
            user.save()

            # ✅ Send Welcome email only after verification
            subject = '🎉 Welcome to SomaSave SACCO'
            html_content = f"""
            <h2 style="color: #1a73e8;">Welcome to SomaSave SACCO!</h2>
            <p>Hello {user.first_name},</p>
            <p>Your account has been successfully verified and created.</p>
            """
            text_content = strip_tags(html_content)

            email_msg = EmailMultiAlternatives(
                subject=subject,
                body=text_content,
                from_email='info@somasave.com',
                to=[user.email],
            )
            email_msg.attach_alternative(html_content, "text/html")
            email_msg.send()

            messages.success(request, 'Email verified successfully! You can now log in.')
            return redirect('login')

        except User.DoesNotExist:
            messages.error(request, 'Invalid OTP. Please try again.')

    return render(request, 'auth/verify_email.html')


# resend OTP
def resend_otp(request):
    if request.method == "POST":
        email = request.POST.get("email") or request.session.get("pending_email")

        try:
            user = User.objects.get(email=email, is_verified=False)

            # generate new OTP
            otp = generate_otp()
            user.otp_code = otp
            user.otp_created_at = timezone.now()
            user.save()

            # send email again
            subject = "🔄 Resend OTP - Verify your SomaSave Account"
            html_content = f"""
            <p>Hello {user.first_name},</p>
            <p>Your new OTP code is: <strong>{otp}</strong></p>
            <p>This code will expire in 10 minutes.</p>
            """
            text_content = strip_tags(html_content)

            email_msg = EmailMultiAlternatives(
                subject=subject,
                body=text_content,
                from_email="info@somasave.com",
                to=[user.email],
            )
            email_msg.attach_alternative(html_content, "text/html")
            email_msg.send()

            messages.success(request, "A new OTP has been sent to your email.")
            return redirect("verify_email")

        except User.DoesNotExist:
            messages.error(request, "We could not find an unverified account with that email.")
            return redirect("register_view")

    return redirect("verify_email")


# logout
@login_required(login_url='login')
def logout_view(request):
    activity_id = request.session.get('login_activity_id')
    if activity_id:
        try:
            activity = LoginActivity.objects.get(id=activity_id)
            activity.logout_time = now()
            activity.save()
        except LoginActivity.DoesNotExist:
            pass  # Do nothing if it fails

    logout(request)
    request.session.flush()  # Clear session completely

    messages.success(request, 'You have been logged out successfully.')
    return redirect('login')




# editing User Profile and updating all details....................................
@login_required(login_url='login')
def edit_profile(request):
    borrower = request.user.borrower_profile  # related_name in Borrower model

    if request.method == "POST":
        # Get form data
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        phone = request.POST.get('phone', '').strip()
        email = request.POST.get('email', '').strip()
        date_of_birth = request.POST.get('date_of_birth', '').strip()
        gender = request.POST.get('gender', '').strip()
        next_of_kin = request.POST.get('next_of_kin', '').strip()
        address = request.POST.get('address', '').strip()
        national_id = request.POST.get('national_id', '').strip()

        # Update user fields
        user = request.user
        user.first_name = first_name
        user.last_name = last_name
        user.email = email
        user.date_of_birth = date_of_birth if date_of_birth else None
        user.gender = gender
        user.next_of_kin = next_of_kin
        user.national_id = national_id
        user.phone_number = phone  # update phone_number on user, NOT borrower.phone (which is a property)
        user.save()

        # Update borrower fields
        borrower.address = address
        borrower.save()

        messages.success(request, "Profile updated successfully.")
        return redirect('userprofile')  # or your actual profile url name

    context = {
        'borrower': borrower,
        'user': request.user,
    }
    return render(request, 'edit/editprofile.html', context)


# uploading profile image
@login_required(login_url='login')
def upload_photo(request):
    if request.method == 'POST' and request.FILES.get('photo'):
        photo = request.FILES['photo']
        borrower = request.user.borrower_profile

        # Upload to Cloudinary
        result = cloudinary.uploader.upload(photo, folder="profile_photos/")

        # Save the Cloudinary URL
        borrower.photo_url = result['secure_url']
        borrower.save()

        messages.success(request, "Profile photo updated successfully.")
        return redirect('userprofile')

    return render(request, 'edit/upload_photo.html')



# CVC and pdf download
def download_statement(request, format):
    user = request.user
    borrower = getattr(user, 'borrower_profile', None)

    # Share Transactions
    share_txns = ShareTransaction.objects.filter(user=user).values(
        'timestamp', 'transaction_type', 'amount', 'status'
    )
    share_data = [
        {
            'date': tx['timestamp'],
            'type': tx['transaction_type'].replace('_', ' ').title(),
            'reference': f"SHR-{tx['timestamp'].strftime('%Y%m%d%H%M%S')}",
            'amount': tx['amount'],
            'status': tx['status'].title()
        } for tx in share_txns
    ]

    # Loan Payments
    payments = Payment.objects.filter(borrower=borrower).select_related('loan').values(
        'id', 'payment_date', 'amount', 'payment_status', 'loan__loan_code'
    )
    payment_data = [
        {
            'date': tx['payment_date'],
            'type': "Loan Repayment",
            'reference': tx['loan__loan_code'] or f"PAY-{tx['id']}",
            'amount': -tx['amount'],
            'status': tx['payment_status'].title()
        } for tx in payments
    ]

    # Deposits
    deposits = Deposit.objects.filter(user=user).values(
        'created_at', 'tx_ref', 'amount', 'status'
    )
    deposit_data = [
        {
            'date': tx['created_at'],
            'type': "Deposit",
            'reference': tx['tx_ref'],
            'amount': tx['amount'],
            'status': tx['status'].title()
        } for tx in deposits
    ]

    # Combine all transactions
    transactions = sorted(
        chain(share_data, payment_data, deposit_data),
        key=lambda x: x['date'],
        reverse=True
    )

    # CSV download
    if format == 'csv':
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="statement.csv"'

        writer = csv.writer(response)
        writer.writerow(['Date', 'Transaction', 'Reference', 'Amount (UGX)', 'Status'])

        for tx in transactions:
            writer.writerow([
                tx['date'].strftime('%Y-%m-%d %H:%M'),
                tx['type'],
                tx['reference'],
                f"{tx['amount']:,.0f}",
                tx['status']
            ])
        return response

    # PDF download
    elif format == 'pdf':
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="statement.pdf"'

        buffer = BytesIO()
        p = canvas.Canvas(buffer)
        p.setFont("Helvetica", 12)
        p.drawString(100, 800, "My Statement")

        y = 780
        for tx in transactions:
            line = f"{tx['date'].strftime('%Y-%m-%d %H:%M')} | {tx['type']} | {tx['reference']} | UGX {tx['amount']:,.0f} | {tx['status']}"
            p.drawString(50, y, line)
            y -= 20
            if y < 50:
                p.showPage()
                y = 800

        p.save()
        buffer.seek(0)
        return HttpResponse(buffer, content_type='application/pdf')

    else:
        return HttpResponse("Invalid format", status=400)

# change password
@login_required
def change_password(request):
    if request.method == 'POST':
        form = CustomPasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important
            messages.success(request, 'Password updated successfully!')
            return redirect('userprofile')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = CustomPasswordChangeForm(user=request.user)
    
    return render(request, 'auth/change_password_modal.html', {'form': form})
