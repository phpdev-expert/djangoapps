from django.contrib import admin
from recruit_api.apps.email.models import Email


class EmailAdmin(admin.ModelAdmin):
    Queries = []
    list_display = ('id', 'subject', 'message', 'email_from', 'recipients_list')
    ordering = ('subject', 'message', 'email_from')
    search_fields = ('subject', 'message', 'email_from')
    list_per_page = 20

    def recipients_list(self, email):
        return "".join([recipient.email for recipient in email.recipients.all()])
    recipients_list.short_description = "Recipients"


admin.site.register(Email, EmailAdmin)

