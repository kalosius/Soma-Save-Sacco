from django.contrib import admin
from .models import Borrower, Loan, Payment, Report

@admin.register(Borrower)
class BorrowerAdmin(admin.ModelAdmin):
    list_display = ['get_name', 'get_email', 'address', 'date_joined']

    def get_name(self, obj):
        return obj.user.get_full_name()
    get_name.short_description = 'Name'

    def get_email(self, obj):
        return obj.user.email
    get_email.short_description = 'Email'

@admin.register(Loan)
class LoanAdmin(admin.ModelAdmin):
    list_display = ['borrower', 'amount', 'interest_rate', 'loan_status', 'start_date', 'due_date', 'loan_code']

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['borrower', 'loan', 'amount', 'payment_date', 'payment_status']

@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ['borrower', 'total_loans', 'total_payments', 'report_date']



admin.site.site_header = "SomaSave SACCO Admin"
admin.site.site_title = "SomaSave Admin Portal"
admin.site.index_title = "Welcome to SomaSave SACCO Admin"