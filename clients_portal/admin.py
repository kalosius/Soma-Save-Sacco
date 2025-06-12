from django.contrib import admin
from . models import CustomUser, ShareTransaction

# Register your models here.
admin.site.register(CustomUser)
admin.site.register(ShareTransaction)

