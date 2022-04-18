from django.apps import apps
from django.contrib import admin
from django.contrib.admin.sites import AlreadyRegistered

from webapp.apps.base.admin import CustomModelAdmin
from webapp.apps.reports.models import UserReportMapping


@admin.register(UserReportMapping)
class UserReportMappingAdmin(CustomModelAdmin):
    model = UserReportMapping
    list_display = ["user_id",  "page_id", "report", "date_created"]
    list_filter = ["user_id"]


app_models = apps.get_app_config('reports').get_models()
for model in app_models:
    try:
        admin.site.register(model, admin_class=CustomModelAdmin)
    except AlreadyRegistered:
        pass