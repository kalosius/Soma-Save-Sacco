from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model, authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.hashers import make_password
from django.contrib.auth.decorators import login_required

# Create your views here.

# loan request
@login_required(login_url='login')
def loanrequest(request):
    return render(request, 'main/loanrequest.html')

# statement
@login_required(login_url='login')
def statement(request):
    return render(request, 'main/mystatement.html')

# shares
@login_required(login_url='login')
def shares(request):
    return render(request, 'main/shares.html')


# loans
@login_required(login_url='login')
def user_loans(request):
    return render(request, 'main/user_loans.html')


# account
@login_required(login_url='login')
def user_account(request):
    return render(request, 'main/account.html')

# userprofile
@login_required(login_url='login')
def userprofile(request):
    return render(request, 'main/userprofile.html')


# dashboard
@login_required(login_url='login')
def client_dashboard(request): 
    return render(request, 'main/client_dashboard.html')

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome! {user.username} Login successful')
            return redirect('client_dashboard')
        else:
            return render(request, 'auth/login.html', {'error': 'Invalid username or password'})
    return render(request, 'auth/login.html')


User = get_user_model()
def register_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        phone_number = request.POST.get('phone_number')
        national_id = request.POST.get('national_id')
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
            national_id=national_id,
            password=make_password(password)  # Hash password manually
        )
        messages.success(request, 'Account created successfully. You can now log in.')
        return redirect('login')
        
    return render(request, 'auth/register.html')


# logout
def logout_view(request):
    logout(request)
    return redirect('login')