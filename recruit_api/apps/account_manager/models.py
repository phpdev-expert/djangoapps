
from django.db import models


class AccountManager(models.Model):
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=150, blank=True)
    date_joined = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Account Manager'
        verbose_name_plural = 'Account Manager(s)'
