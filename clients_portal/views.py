from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import get_user_model, authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.hashers import make_password
from django.contrib.auth.decorators import login_required
from .models import ShareTransaction, Account, generate_unique_account_number
from django.contrib.auth.models import User
from adminapp.models import Loan, Payment, Borrower, RepaymentSchedule
from django.db.models import Sum, F, Value, CharField
from datetime import timedelta
import random
from django.utils import timezone
from decimal import Decimal
from datetime import datetime
from django.views.decorators.http import require_POST
from django.db.models import Q
from django.utils.dateparse import parse_date
from itertools import chain






# Create your views here.

# transactions
@login_required(login_url='login')
def transactions(request):
    return render(request, 'main/transactions.html')

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

    # GET filters
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
            'amount': -tx['amount'],  # repayments are outflows
            'status': tx['payment_status'].title()
        } for tx in payments
    ]

    # Combine
    transactions = sorted(
        chain(share_data, payment_data),
        key=lambda x: x['date'],
        reverse=True
    )

    # Filters
    if start_date:
        transactions = [tx for tx in transactions if tx['date'].date() >= datetime.strptime(start_date, "%Y-%m-%d").date()]
    if end_date:
        transactions = [tx for tx in transactions if tx['date'].date() <= datetime.strptime(end_date, "%Y-%m-%d").date()]
    if transaction_type:
        transactions = [tx for tx in transactions if tx['type'].lower().replace(" ", "_") == transaction_type]

    context = {
        'transactions': transactions,
    }
    return render(request, 'main/mystatement.html', context)



# shares
SHARE_VALUE = 200000  # Current share value in UGX
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
    total_savings = Decimal('2500000.00')  # Replace with actual logic
    share_capital = ShareTransaction.objects.filter(user=user).aggregate(total=Sum('amount'))['total'] or 0
    outstanding_loan = Loan.objects.filter(borrower=borrower, loan_status='Approved').aggregate(
        total=Sum('amount'))['total'] or 0
    dividends_earned = Decimal('150000.00')  # Replace with logic

    # Transactions
    transactions = list(ShareTransaction.objects.filter(user=user).values(
        'timestamp', 'transaction_type', 'amount', 'status')) + \
        list(Payment.objects.filter(borrower=borrower).values(
            'payment_date', 'amount', 'payment_status'))

    normalized_transactions = [
        {
            'date': tx.get('timestamp') or tx.get('payment_date'),
            'type': tx.get('transaction_type') or 'Loan Repayment',
            'amount': tx['amount'],
            'status': tx.get('status') or tx.get('payment_status'),
        }
        for tx in transactions
    ]
    normalized_transactions.sort(key=lambda x: x['date'], reverse=True)

    context = {
        'account_number': account.account_number,
        'account_type': "Savings Account",
        'member_since': borrower.date_joined.strftime('%A, %B %d, %Y'),
        'total_savings': total_savings,
        'share_capital': share_capital,
        'outstanding_loan': outstanding_loan,
        'dividends_earned': dividends_earned,
        'account_balance': account.balance,
        'recent_transactions': normalized_transactions[:5],
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
    current_hour = datetime.now().hour

    context = {
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
    }

    return render(request, 'main/client_dashboard.html', context)




def login_view(request):
    if request.method == 'POST':
        identifier = request.POST.get('username')  # could be username or email
        password = request.POST.get('password')

        # Try to find a user by email if input looks like an email
        if '@' in identifier:
            try:
                user_obj = User.objects.get(email=identifier)
                username = user_obj.username
            except User.DoesNotExist:
                username = None
        else:
            username = identifier

        if username:
            user = authenticate(request, username=username, password=password)
        else:
            user = None

        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome! {user.username} Login successful')
            return redirect('client_dashboard')
        else:
            return render(request, 'auth/login.html', {'error': 'Invalid username/email or password'})
    
    return render(request, 'auth/login.html')



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

        if password != confirm_password:
            return render(request, 'auth/register.html', {'error': 'Passwords do not match'})

        if User.objects.filter(username=username).exists():
            return render(request, 'auth/register.html', {'error': 'Username already taken'})

        if User.objects.filter(email=email).exists():
            return render(request, 'auth/register.html', {'error': 'Email already in use'})

        user = User.objects.create(
            username=username,
            email=email,
            phone_number=phone_number,
            first_name=first_name,
            last_name=last_name,
            password=make_password(password)
        )

        Borrower.objects.create(user=user)

        messages.success(request, 'Account created successfully. You can now log in.')
        return redirect('login')

    return render(request, 'auth/register.html')

# logout
@login_required(login_url='login')
def logout_view(request):
    logout(request)
    return redirect('login')




# editing User Profile and updating all details....................................
@login_required
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
@login_required
def upload_photo(request):
    if request.method == 'POST' and request.FILES.get('photo'):
        photo = request.FILES['photo']
        borrower = request.user.borrower_profile
        borrower.photo = photo  # assuming your Borrower model has a ImageField named 'photo'
        borrower.save()
        messages.success(request, "Profile photo updated successfully.")
        return redirect('userprofile')  # or your profile page url name

    return render(request, 'edit/upload_photo.html')

