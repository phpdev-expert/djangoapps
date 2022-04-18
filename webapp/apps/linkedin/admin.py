from django.contrib import admin

from webapp.apps.base.admin import CustomModelAdmin
from webapp.apps.linkedin import models
# Register your models here.


@admin.register(models.Page)
class AdminPage(CustomModelAdmin):
    """
    Page admin
    """
    list_display = [
        "user_id",
        "page_id",
        "name"

    ]
    search_fields = [
        "page_id",
    ]


@admin.register(models.PageStats)
class AdminPageStats(CustomModelAdmin):
    """
    Page Stats admin
    """
    list_display = [
        "page",
    ]
    search_fields = [
        "page",
    ]


@admin.register(models.PostStats)
class AdminPageStats(CustomModelAdmin):
    """
    Page Post Stats admin
    """
    list_display = [
        "urn",
        "text",
        "post_date"
    ]
    search_fields = [
        "urn",
    ]