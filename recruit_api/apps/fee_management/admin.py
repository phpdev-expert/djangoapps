from django.contrib import admin
from .models import Fee


class FeeAdmin(admin.ModelAdmin):
    list_display = ('id', 'account_manager')

admin.site.register(Fee, FeeAdmin)

