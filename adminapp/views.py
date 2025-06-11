from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Borrower, Loan, Payment, Report
from django.utils import timezone
from datetime import timedelta
from datetime import datetime
from django.db.models import Sum, Count


# Create your views here.
def dashboard(request):
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
def add_borrower(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        address = request.POST.get('address')

        if name and email and phone and address:
            # Add uniqueness check for email or phone
            if Borrower.objects.filter(email=email).exists():
                messages.error(request, 'Email already exists.')
            elif Borrower.objects.filter(phone=phone).exists():
                messages.error(request, 'Phone number already exists.')
            else:
                Borrower.objects.create(
                    name=name,
                    email=email,
                    phone=phone,
                    address=address
                )
                messages.success(request, 'Borrower added successfully!')
                return redirect('borrowers') 
        else:
            messages.error(request, 'All fields are required.')
    return render(request, 'main/add_borrower.html')

# all borrowers display
def borrowers(request):
    all_borrowers = Borrower.objects.all()
    return render(request, 'main/borrowers.html', {'borrowers': all_borrowers})



# adding a loan
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


def loans(request):
    loans = Loan.objects.select_related('borrower').all()
    return render(request, 'main/loans.html', {'loans': loans})

def payments(request):
    return render(request, 'main/payments.html')


# making a loan payment
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

def reports(request):
    return render(request, 'main/reports.html')




# editing and deleting
def edit_borrower(request, id):
    borrower = get_object_or_404(Borrower, id=id)
    if request.method == 'POST':
        # Update borrower information
        borrower.name = request.POST.get('name')
        borrower.email = request.POST.get('email')
        borrower.phone = request.POST.get('phone')
        borrower.address = request.POST.get('address')
        borrower.save()
        messages.success(request, 'Borrower updated successfully!')
        return redirect('borrowers')
    return render(request, 'edit/edit_borrower.html', {'borrower': borrower})


def delete_borrower(request, id):
    borrower = get_object_or_404(Borrower, id=id)
    borrower.delete()
    messages.success(request, 'Borrower deleted successfully!')
    return redirect('borrowers')


# editing and deleting loans
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
def delete_loan(request, id):
    loan = get_object_or_404(Loan, id=id)
    loan.delete()
    messages.success(request, 'Loan deleted successfully.')
    return redirect('loans')