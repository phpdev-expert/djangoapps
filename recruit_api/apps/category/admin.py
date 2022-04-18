from django.contrib import admin
from recruit_api.apps.category.models import Category


class CategoryAdmin(admin.ModelAdmin):
    Queries = []
    list_display = ('id', 'title')
    ordering = ('title',)
    search_fields = ('title',)
    list_per_page = 20


admin.site.register(Category, CategoryAdmin)

