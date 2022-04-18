import time

from celery import shared_task
from django.conf import settings
from datetime import datetime
from webapp.apps.metrics.models import Account
from webapp.apps.reports.models import Reports, UserReportMapping, PerformanceConfig

@shared_task(bind=True, name=settings.DELETE_USER_TASK)
def delete_user(self, userid=None):
    print("delete user", userid)
    if userid:
        try:
            #remove all the report and related data of an user
            user_reports = list(UserReportMapping.objects.filter(user_id=userid).values_list("report", flat=True))
            Reports.objects.filter(id__in = user_reports).delete()
            #remove all performace config of an user
            PerformanceConfig.objects.filter(user_id=userid).delete()
            #remove all the accounts and releated data of an user
            Account.objects.filter(user_id = userid).delete()
        except Exception as msg:
            print(msg)