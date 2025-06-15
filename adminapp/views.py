from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Borrower, Loan, Payment, Report
from django.utils import timezone
from datetime import timedelta
from datetime import datetime
from django.db.models import Sum, Count, F, Value, CharField
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.db.models.functions import Concat
from django.contrib.auth import get_user_model
from django.utils.crypto import get_random_string


# redirecting to login if not superuser
def superuser_required(view_func):
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_superuser:
            return redirect('not_authorized')  # Change to any URL or view you prefer
        return view_func(request, *args, **kwargs)
    return _wrapped_view




# Create your views here.

@superuser_required
def dashboard(request):
    active_loans_count = Loan.objects.filter(loan_status='Approved').count()
    repaid_loans_count = Payment.objects.values('loan').distinct().count()
    loan_applications_count = Loan.objects.count()
    total_revenue = Payment.objects.aggregate(total=Sum('amount'))['total'] or 0

    # Top Borrowers with related user fields
    top_borrowers = (
        Loan.objects.select_related('borrower__user')
        .annotate(
            borrower_name=Concat(
                F('borrower__user__first_name'),
                Value(' '),
                F('borrower__user__last_name'),
                output_field=CharField()
            )
        )
        .order_by('-amount')[:5]
    )

    recent_activities = Payment.objects.select_related('borrower__user', 'loan').order_by('-payment_date')[:5]

    return render(request, 'main/dashboard.html', {
        'active_loans': active_loans_count,
        'repaid_loans': repaid_loans_count,
        'loan_applications': loan_applications_count,
        'total_revenue': total_revenue,
        'top_borrowers': top_borrowers,
        'recent_activities': recent_activities,
    })

    # Card Data
    active_loans_count = Loan.objects.filter(loan_status='Approved').count()
    repaid_loans_count = Payment.objects.values('loan').distinct().count()
    loan_applications_count = Loan.objects.all().count()
    total_revenue = Payment.objects.aggregate(total=Sum('amount'))['total'] or 0

    # Top Borrowers - sort by total loan amount
    top_borrowers = (
        Loan.objects
        .values('id', 'loan_code', 'borrower__name', 'amount', 'interest_rate', 'start_date')
        .order_by('-amount')[:5]
    )

    # Recent Loan Activities (mock or build from Payment & Loan events)
    recent_activities = Payment.objects.select_related('borrower', 'loan').order_by('-payment_date')[:5]

    return render(request, 'main/dashboard.html', {
        'active_loans': active_loans_count,
        'repaid_loans': repaid_loans_count,
        'loan_applications': loan_applications_count,
        'total_revenue': total_revenue,
        'top_borrowers': top_borrowers,
        'recent_activities': recent_activities,
    })



# adding a borrower
User = get_user_model()
@superuser_required
def add_borrower(request):
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        address = request.POST.get('address')

        if not user_id or not address:
            messages.error(request, 'All fields are required.')
            return redirect('add_borrower')

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            messages.error(request, 'Selected user does not exist.')
            return redirect('add_borrower')

        if Borrower.objects.filter(user=user).exists():
            messages.error(request, 'This user is already registered as a borrower.')
        else:
            Borrower.objects.create(user=user, address=address)
            messages.success(request, 'Borrower added successfully!')
            return redirect('borrowers')

    # Get users who are NOT already borrowers
    borrower_user_ids = Borrower.objects.values_list('user_id', flat=True)
    available_users = User.objects.exclude(id__in=borrower_user_ids)

    return render(request, 'main/add_borrower.html', {'users': available_users})


# all borrowers display
@superuser_required
def borrowers(request):
    all_borrowers = Borrower.objects.all()
    return render(request, 'main/borrowers.html', {'borrowers': all_borrowers})



# adding a loan
@superuser_required
def add_loan(request):
    borrowers = Borrower.objects.all()

    if request.method == 'POST':
        borrower_id = request.POST.get('borrower_id')
        amount = request.POST.get('amount')
        interest_rate = request.POST.get('interest_rate')
        loan_status = request.POST.get('loan_status')  # Optional if needed

        try:
            borrower = Borrower.objects.get(id=borrower_id)
            loan = Loan.objects.create(
                borrower=borrower,
                amount=amount,
                interest_rate=interest_rate,
                loan_status=loan_status,
                due_date=timezone.now() + timedelta(days=30)  # example due date
            )
            messages.success(request, "Loan created successfully.")
            return redirect('add_loan')  # or wherever you want to redirect
        except Borrower.DoesNotExist:
            messages.error(request, "Borrower not found.")
        except Exception as e:
            messages.error(request, f"Error: {e}")
    return render(request, 'main/add_loan.html', {'borrowers': borrowers})


@superuser_required
def loans(request):
    loans = Loan.objects.select_related('borrower').all()
    return render(request, 'main/loans.html', {'loans': loans})

@superuser_required
def payments(request):
    all_payments = Payment.objects.select_related('loan').all().order_by('-payment_date')
    return render(request, 'main/payments.html', {'payments': all_payments})


# making a loan payment
@superuser_required
def add_payment(request):
    if request.method == 'POST':
        loan_code = request.POST.get('loan_code')
        payment_date = request.POST.get('payment_date')
        amount = request.POST.get('amount')
        payment_status = request.POST.get('payment_status')

        try:
            loan = Loan.objects.get(loan_code=loan_code)
        except Loan.DoesNotExist:
            messages.error(request, "Loan with this code does not exist.")
            return redirect('add_payment')

        try:
            payment_date_obj = datetime.strptime(payment_date, '%Y-%m-%d').date()
        except ValueError:
            messages.error(request, "Invalid payment date format.")
            return redirect('add_payment')

        try:
            amount_val = float(amount)
        except (TypeError, ValueError):
            messages.error(request, "Invalid amount.")
            return redirect('add_payment')

        # Create payment linked to loan and borrower
        payment = Payment.objects.create(
            borrower=loan.borrower,
            loan=loan,
            amount=amount_val,
            payment_date=payment_date_obj,
            payment_status=payment_status
        )

        messages.success(request, f"Payment recorded successfully for loan {loan_code}.")
        return redirect('payments')  # or wherever you want to redirect after success

    return render(request, 'main/add_payment.html')



@superuser_required
def reports(request):
    return render(request, 'main/reports.html')


# editing borrower
@superuser_required
def edit_borrower(request, id):
    borrower = get_object_or_404(Borrower, id=id)
    user = borrower.user

    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone_number = request.POST.get('phone')
        address = request.POST.get('address')

        # Check if email already exists for another user
        if User.objects.filter(email=email).exclude(id=user.id).exists():
            messages.error(request, 'Email already exists.')
            return render(request, 'edit/edit_borrower.html', {'borrower': borrower})

        # Check if phone number already exists for another user
        if User.objects.filter(phone_number=phone_number).exclude(id=user.id).exists():
            messages.error(request, 'Phone number already exists.')
            return render(request, 'edit/edit_borrower.html', {'borrower': borrower})

        # Update User fields
        user.first_name = name
        user.email = email
        user.phone_number = phone_number
        user.save()

        # Update Borrower fields
        borrower.address = address
        borrower.save()

        messages.success(request, 'Borrower updated successfully!')
        return redirect('borrowers')

    return render(request, 'edit/edit_borrower.html', {'borrower': borrower})

# deleting borrower
@superuser_required
def delete_borrower(request, id):
    borrower = get_object_or_404(Borrower, id=id)
    borrower.delete()
    messages.success(request, 'Borrower deleted successfully!')
    return redirect('borrowers')


# editing and deleting loans
@superuser_required
def edit_loan(request, id):
    loan = get_object_or_404(Loan, id=id)
    
    if request.method == 'POST':
        try:
            loan.amount = request.POST.get('amount')
            loan.interest_rate = request.POST.get('interest_rate')
            loan.due_date = request.POST.get('due_date')
            loan.loan_status = request.POST.get('loan_status')
            loan.save()
            messages.success(request, 'Loan updated successfully.')
            return redirect('loans')
        except Exception as e:
            messages.error(request, f'Error updating loan: {e}')
    
    return render(request, 'edit/edit_loan.html', {'loan': loan})


# Delete Loan View
@superuser_required
def delete_loan(request, id):
    loan = get_object_or_404(Loan, id=id)
    loan.delete()
    messages.success(request, 'Loan deleted successfully.')
    return redirect('loans')






# admin only form

def admin_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None and (user.is_staff or user.is_superuser):
            login(request, user)
            messages.success(request, f'Welcome back, {user.username.capitalize()}!')
            return redirect('dashboard')  # Change this to your desired admin landing page
        else:
            messages.error(request, 'Invalid credentials or not authorized as admin.')
            return redirect('admin_login')
    return render(request, 'main/auth/login.html')


@login_required(login_url='admin_login')
def admin_logout(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('admin_login')


# views.py
def not_authorized(request):
    return render(request, 'main/auth/not_authorized.html')
