from managements.models import UserRoles
from django.contrib import admin
from managements.models import UserGroup, AdminUsers
import hashlib

class UserRolesAdmin(admin.ModelAdmin):
    list_display = ('name','created_by','create_dtm')
    def created_by(self, obj):
        return AdminUsers.objects.get(id=obj.create_by).username
    def has_delete_permission(self, request, obj=None):
        return False
    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.create_by = request.user.id
        else:
            obj.last_modified_by = request.user.id
        super().save_model(request, obj, form, change)



class UserGroupAdmin(admin.ModelAdmin):
    list_display = ('name','created_by','create_dtm')
    def created_by(self, obj):
        return AdminUsers.objects.get(id=obj.create_by).username
    def has_delete_permission(self, request, obj=None):
        return False

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.create_by = request.user.id
        else:
            obj.last_modified_by = request.user.id
        super().save_model(request, obj, form, change)



class AdminUsersAdmin(admin.ModelAdmin):
    list_display = ('username', 'email','first_name','last_name')
    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.create_by = request.user.id
            obj.set_password(obj.password)
        else:
            orig_obj = AdminUsers.objects.get(pk=obj.pk)
            if obj.password != orig_obj.password:
                obj.set_password(obj.password)
            obj.last_modified_by = request.user.id
        super().save_model(request, obj, form, change)



admin.site.register(UserRoles,UserRolesAdmin)
admin.site.register(UserGroup,UserGroupAdmin)
admin.site.register(AdminUsers,AdminUsersAdmin)
