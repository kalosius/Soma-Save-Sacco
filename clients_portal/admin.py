from django.contrib import admin
from .models import CustomUser, ShareTransaction, Account, LoginActivity, Deposit, NationalIDVerification


admin.site.register(NationalIDVerification)

@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    pass


@admin.register(ShareTransaction)
class ShareTransactionAdmin(admin.ModelAdmin):
    list_display = ('user', 'transaction_type', 'number_of_shares', 'amount', 'timestamp')
    list_filter = ('transaction_type', 'status', 'timestamp')
    search_fields = ('user__username', 'user__email')


@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ('account_number', 'user', 'account_type', 'date_created')


@admin.register(Deposit)
class DepositAdmin(admin.ModelAdmin):
    list_display = ('user', 'tx_ref', 'amount', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('user__username', 'tx_ref')




@admin.register(LoginActivity)
class LoginActivityAdmin(admin.ModelAdmin):
    list_display = ('user', 'ip_address', 'location', 'device', 'login_time', 'logout_time')
    list_filter = ('login_time', 'location')
    search_fields = ('user__username', 'ip_address', 'location', 'device')
