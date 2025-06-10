from django.contrib import admin
from . models import Borrower, Loan, Payment, Report
# Register your models here.
admin.site.site_header = "SomaSave SACCO Admin"
admin.site.site_title = "SomaSave SACCO Admin Portal"
admin.site.index_title = "Welcome to SomaSave SACCO Admin Portal"



@admin.register(Borrower)
class BorrowerAdmin(admin.ModelAdmin):
    list_display = ['name', 'email']  # customize fields here

@admin.register(Loan)
class LoanAdmin(admin.ModelAdmin):
    list_display = ['borrower', 'amount', 'interest_rate', 'loan_status', 'start_date', 'due_date', 'loan_code']

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['borrower', 'loan', 'amount', 'payment_date', 'payment_status']

@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ['borrower', 'total_loans', 'total_payments', 'report_date']
