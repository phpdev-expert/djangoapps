from django.db import models
from model_utils.models import TimeStampedModel
from django.utils import timezone
from django.contrib.auth.models import (AbstractBaseUser,PermissionsMixin)
from django.db import models
from django.forms import ModelForm
from django.contrib.auth.models import UserManager
from django.contrib.auth.models import User

from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.base_user import AbstractBaseUser
from model_utils.models import TimeStampedModel

from django.contrib.auth.models import UserManager
from django.contrib.auth.signals import user_logged_in, user_logged_out, user_login_failed
from django.dispatch import receiver



STATUS_CHOICES = (
   ('1', 'Active'),
   ('0', 'In Active')
)


class UserRoles(models.Model):
    name = models.CharField(max_length=80)
    create_by=models.IntegerField(editable=False)
    last_modified_by=models.IntegerField(editable=False)
    create_dtm=models.DateTimeField(auto_now_add=True)
    last_modified_dtm=models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'User Role'
        verbose_name_plural = 'User Roles'

    def __str__(self):
        return self.name


class LastPasswords(models.Model):
    user_id = models.IntegerField()
    last_passwords= models.CharField(max_length=250)
    create_dtm=models.DateTimeField(auto_now_add=True)
    class Meta:
       managed = False
       db_table = 'last_passwords'



class UserGroup(models.Model):
    name = models.CharField(max_length=80)
    create_by=models.IntegerField(editable=False)
    last_modified_by=models.IntegerField(editable=False)
    create_dtm=models.DateTimeField(auto_now_add=True)
    last_modified_dtm=models.DateTimeField(auto_now=True)
    class Meta:
        verbose_name = 'User Group'
        verbose_name_plural = 'User Groups'

    def __str__(self):
        return self.name




class AdminUsers(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=150,unique=True)
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)
    department = models.CharField(max_length=100, blank=True)
    position = models.CharField(max_length=100, blank=True)
    is_superuser = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_active=models.BooleanField(default=True,blank=True,)
    last_login=models.DateTimeField(auto_now=True)
    login_faild=models.IntegerField()
    is_login=models.IntegerField()
    last_password_change=models.DateTimeField(null=True, blank=True)
    role_id=models.ForeignKey(UserRoles, on_delete=models.CASCADE,null=True, blank=True)
    group_id=models.ForeignKey(UserGroup, on_delete=models.CASCADE)
    create_by=models.CharField(max_length=50, blank=True, editable=False)
    last_modified_by=models.CharField(max_length=50, blank=True, editable=False)
    create_dtm=models.DateTimeField(auto_now_add=True)
    last_modified_dtm=models.DateTimeField(auto_now=True)

    objects = UserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email','password']

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'User(s)'
        ordering = ['username']



@receiver(user_login_failed)
def user_login_failed_callback(sender, credentials, **kwargs):
    try:
        lu=AdminUsers.objects.filter(username=credentials.get('username', None)).get()
        if lu:
            if lu.login_faild:
                lu.login_faild=int(lu.login_faild)+1
            else:
                lu.login_faild=1
            if lu.login_faild>=5:
                lu.is_active=False
            lu.save()
    except AdminUsers.DoesNotExist:
        return True

@receiver(user_logged_in)
def user_logged_in_callback(sender, request, user, **kwargs):
    lu=AdminUsers.objects.filter(username=user.username).get()
    lu.login_faild=0
    lu.save()
