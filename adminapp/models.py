from django.db import models
from django.utils import timezone
import random
from clients_portal.models import CustomUser  # Reference from accounts app


class Borrower(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='borrower_profile')
    address = models.CharField(max_length=255)
    date_joined = models.DateTimeField(auto_now_add=True)
    photo_url = models.URLField(null=True, blank=True)  # ✅ use URLField instead of ImageField


    def __str__(self):
        return f"{self.user.get_full_name()} (User: {self.user.username})"

    @property
    def email(self):
        return self.user.email

    @property
    def phone(self):
        return self.user.phone_number


class Loan(models.Model):
    borrower = models.ForeignKey(Borrower, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2)
    loan_status = models.CharField(max_length=20, choices=[
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
        ('Cleared', 'Cleared')
    ])
    start_date = models.DateTimeField(auto_now_add=True)
    due_date = models.DateTimeField()
    loan_code = models.CharField(max_length=7, unique=True, editable=False)

    def save(self, *args, **kwargs):
        if not self.loan_code:
            self.loan_code = self.generate_unique_code()
        super().save(*args, **kwargs)

    def generate_unique_code(self):
        while True:
            code = str(random.randint(1000000, 9999999))  # 7-digit code
            if not Loan.objects.filter(loan_code=code).exists():
                return code

    def __str__(self):
        return f"Loan #{self.loan_code} for {self.borrower}"


class Payment(models.Model):
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]
    borrower = models.ForeignKey(Borrower, on_delete=models.CASCADE)
    loan = models.ForeignKey(Loan, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateTimeField(default=timezone.now)
    payment_status = models.CharField(max_length=20,choices=PAYMENT_STATUS_CHOICES,default='pending')
    def __str__(self):
        return f"Payment {self.amount} by {self.borrower}"


class Report(models.Model):
    borrower = models.ForeignKey(Borrower, on_delete=models.CASCADE)
    total_loans = models.DecimalField(max_digits=10, decimal_places=2)
    total_payments = models.DecimalField(max_digits=10, decimal_places=2)
    report_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Report for {self.borrower} on {self.report_date.strftime('%Y-%m-%d')}"


# Repayment schedule
class RepaymentSchedule(models.Model):
    loan = models.ForeignKey(Loan, on_delete=models.CASCADE)
    installment_number = models.IntegerField()
    due_date = models.DateField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=[
        ('Paid', 'Paid'),
        ('Upcoming', 'Upcoming'),
        ('Overdue', 'Overdue')
    ])

    def __str__(self):
        return f"Loan {self.loan.id} - Installment {self.installment_number}"
