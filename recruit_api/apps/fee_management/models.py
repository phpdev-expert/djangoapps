from django.db import models
from recruit_api.apps.core.user.models.user import User
from recruit_api.apps.account_manager.models import AccountManager
from recruit_api.apps.client.models.client import Client
from recruit_api.apps.job.models.job import Job


class Fee(models.Model):
    # recruiter = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    account_manager = models.ForeignKey(AccountManager, on_delete=models.CASCADE, null=True, blank=True)
    # client = models.ForeignKey(Client, on_delete=models.CASCADE, null=True, related_name="fee_client")
    # job = models.ForeignKey(Job, on_delete=models.CASCADE, null=True)
    client_fee_percentage = models.IntegerField('Client Fee Percentage', blank=True, null=True)
    client_fee_amount = models.IntegerField('Client Fee Amount', blank=True, null=True)
    rc_commission_percent = models.IntegerField('RC Commission percent', blank=True, null=True)
    am_commission_percent = models.IntegerField('AM Commission percent', blank=True, null=True)

