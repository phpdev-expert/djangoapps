from django.contrib import admin
from recruit_api.apps.core.user.models import User


class UserAdmin(admin.ModelAdmin):
    Queries = []
    list_display = ('id', 'email', 'username', 'is_active', 'is_superuser', 'is_staff')
    fields = ('email', 'password', 'username', 'is_active', 'is_superuser', 'is_staff')
    ordering = ('email', 'username')
    search_fields = ('email', 'username')
    list_per_page = 20
    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.set_password(obj.password)
        else:
            orig_obj = User.objects.get(pk=obj.pk)
            if obj.password != orig_obj.password:
                obj.set_password(obj.password)
        super().save_model(request, obj, form, change)
admin.site.register(User, UserAdmin)
