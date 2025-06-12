from django.contrib import admin
from . models import CustomUser, ShareTransaction

# Register your models here.
admin.site.register(CustomUser)


class ShareTransactionAdmin(admin.ModelAdmin):
    list_display = ('user', 'transaction_type', 'number_of_shares', 'amount', 'timestamp')  # 👈 add timestamp
    list_filter = ('transaction_type', 'status', 'timestamp')  # optional: filter by time
    search_fields = ('user__username', 'user__email')

admin.site.register(ShareTransaction, ShareTransactionAdmin)

