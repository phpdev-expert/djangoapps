from django.db.models.signals import post_save
from django.db import transaction

from webapp.apps.api.serializers.accounts import AccountSignalResponseSerializer
from webapp.apps.metrics.models import Account
from django.dispatch import receiver

from webapp.apps.metrics.tasks import linkedin_saved_task, twitter_sync_task, facebook_sync_task
from webapp.apps.metrics.tasks.instagram import instagram_business_sync_task

from webapp.apps.api.serializers.reports import ReportSerializer
from webapp.apps.reports.models import UserReportMapping

# def create_default_report(sender, instance, update_fields, **kwargs):
#     if (kwargs["created"]):
#         # by default create custom report for new account
#         reports = UserReportMapping.objects.filter(user_id = instance.user_id)
#         if not reports:
#             payload = {"platform":"custom", "title":"custom_report","report_user_id": instance.user_id}
#             report = ReportSerializer(data=payload)
#             if report.is_valid():
#                 report.save()
@receiver(post_save, sender=Account)
def save_account_status(sender, instance, update_fields, **kwargs):
    #transaction.on_commit(lambda:create_default_report(sender, instance, update_fields, **kwargs))
    # if (kwargs["created"]):
    #     # by default create custom report for new account
    #     reports = UserReportMapping.objects.filter(user_id = instance.user_id)
    #     if not reports:
    #         payload = {"platform":"custom", "title":"custom_report","report_user_id": instance.user_id}
    #         report = ReportSerializer(data=payload)
    #         if report.is_valid():
    #             report.save()
    if update_fields:
        if instance.status == "revoked" and "status" in list(update_fields):
            if instance.type == "linkedin":
                linkedin_saved_task.delay(data=AccountSignalResponseSerializer(instance=instance).data)

            if instance.type == "twitter":
                twitter_sync_task.delay(data=AccountSignalResponseSerializer(instance=instance).data)

            if instance.type == "facebook":
                facebook_sync_task.delay(data=AccountSignalResponseSerializer(instance=instance).data)

            if instance.type == "instagram":
                instagram_business_sync_task.delay(data=AccountSignalResponseSerializer(instance=instance).data)