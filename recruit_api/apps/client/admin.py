from django.contrib import admin
from recruit_api.apps.client.models import Client
from recruit_api.apps.client.models.client import Contact


class ClientAdmin(admin.ModelAdmin):
    Queries = []
    list_display = ('id', 'name', 'location', 'founded_year', 'website', 'employee_count')
    ordering = ('id', 'name', 'location', 'founded_year', 'website', 'employee_count')
    search_fields = ('id', 'name', 'location', 'founded_year', 'website', 'employee_count')
    list_per_page = 20


admin.site.register(Client, ClientAdmin)


class ContactAdmin(admin.ModelAdmin):
    pass
admin.site.register(Contact, ContactAdmin)