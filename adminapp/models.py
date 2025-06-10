from django.db import models
import random
from django.utils import timezone


# Create your models here.
class Borrower(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15, unique=True)
    address = models.CharField(max_length=255)
    date_joined = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
    
class Loan(models.Model):
    borrower = models.ForeignKey(Borrower, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2)
    loan_status = models.CharField(max_length=20, choices=[
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected')
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
        return f"Loan for {self.borrower.name} - Amount: {self.amount}"
    

class Payment(models.Model):
    borrower = models.ForeignKey(Borrower, on_delete=models.CASCADE)
    loan = models.ForeignKey(Loan, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    # payment_date = models.DateField()  # Changed from DateTimeField to DateField, no auto_now_add
    payment_date = models.DateTimeField(default=timezone.now)
    payment_status = models.CharField(max_length=20)

    def __str__(self):
        return f"Payment of {self.amount} by {self.borrower.name} for Loan ID: {self.loan.id}"
    
class Report(models.Model):
    borrower = models.ForeignKey(Borrower, on_delete=models.CASCADE)
    total_loans = models.DecimalField(max_digits=10, decimal_places=2)
    total_payments = models.DecimalField(max_digits=10, decimal_places=2)
    report_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Report for {self.borrower.name} - Total Loans: {self.total_loans}, Total Payments: {self.total_payments}"
    