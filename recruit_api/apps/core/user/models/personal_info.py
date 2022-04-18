from __future__ import unicode_literals

from django.db import models
from model_utils.models import TimeStampedModel
from recruit_api.apps.core.user.models import User


class PersonalInfo(TimeStampedModel):
    first_name = models.CharField(max_length=150, blank=True, null=True)
    last_name = models.CharField(max_length=150, blank=True, null=True)
    phone_number = models.CharField(max_length=30, blank=True, null=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    class Meta:
        app_label = 'user'

    @property
    def email(self):
        """
        Returns the email of the user
        """
        return self.user.email

    @property
    def full_name(self):
        """
        Returns the first_name plus the last_name, with a space in between.
        """
        full_name = '%s %s' % (self.first_name or "", self.last_name or "")
        return full_name.strip()

    @property
    def short_name(self):
        """
        Returns the short name for the user.
        """
        return self.first_name or ""
