from django.contrib import admin
from recruit_api.apps.account_manager.models import AccountManager


class AccountManagerAdmin(admin.ModelAdmin):
    list_display = ('id', 'username',)


admin.site.register(AccountManager, AccountManagerAdmin)

