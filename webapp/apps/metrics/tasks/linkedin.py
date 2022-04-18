import time

from celery import shared_task
from django.conf import settings
from datetime import datetime
from webapp.apps.metrics.data_loader.linkedin import LinkedinDataLoader
from webapp.apps.api.cache import Cacher

import logging

log = logging.getLogger("linkedin")

@shared_task(bind=True, name=settings.LINKEDIN_PAGE_SYNC_ACTION_TASK)
def linkedin_sync_action_task(self, data=None):
    log.info("linkedin_sync_action_task")
    log.info(data)
    if data:
        user_id = data.get('auth_user_id')
        page_id = data.get('page_id')
        dataLoader = LinkedinDataLoader(user_id=user_id, page_id=page_id)
        page = dataLoader.get_page(user_id=user_id, page_id=page_id)
        page.sync_status = "progress"
        page.save()
        try:
            dataLoader.fetch_insights()
        except Exception as exc:
            log.info(f"linkedin fetch insights failed {str(exc)}")
        try:
            linkedin_sync_post(user_id=user_id, page_id=page_id)
        except Exception as exc:
            log.info(f"linkedin sync post failed {str(exc)}")
        page = dataLoader.get_page(user_id=user_id, page_id=page_id)
        now = datetime.now()
        page.sync_completed = now.strftime("%Y-%m-%d %H:%M:%S")
        if page.sync_status == "pending" or page.sync_status == "progress":
            page.error = ""
            page.sync_status = "ok"
        page.save()
        Cacher.delete(f"stat_health_{user_id}")
        Cacher.delete_pattern(('metrics_{}_*').format(user_id))

@shared_task(bind=True, name=settings.LINKEDIN_PAGE_SYNC_TASK)
def linkedin_saved_task(self, data=None):
    log.info("linkedin_page_sync")
    log.info(data)
    if data:
        status = data.get("status")
        user_id = data.get('auth_user_id')
        page_id = data.get('page_id')
        if status == "deleted":
            dataLoader = LinkedinDataLoader(user_id=user_id, page_id=page_id)
            try:
                dataLoader.save_page(data=data)
                Cacher.delete(f"stat_health_{user_id}")
            except Exception as exc:
                log.info(exc)
        if status == "active":
            dataLoader = LinkedinDataLoader(user_id=user_id, page_id=page_id)
            try:
                dataLoader.save_page(data=data)
                linkedin_sync_action_task.delay(data)
            except Exception as exc:
                log.info(exc)
        #     try:
        #         dataLoader.fetch_insights()
        #     except Exception as exc:
        #         log.info(exc)
        #     try:
        #         linkedin_sync_post(user_id=user_id, page_id=page_id)
        #     except Exception as exc:
        #         log.info(exc)
        #     page = dataLoader.get_page(user_id=user_id, page_id=page_id)
        #     now = datetime.now()
        #     page.sync_completed = now.strftime("%Y-%m-%d %H:%M:%S")
        #     page.save()
        # Cacher.delete(f"stat_health_{user_id}")


# @shared_task(bind=True, name=settings.LINKEDIN_SYNC_POST_ANALYTICS)
def linkedin_sync_post(user_id, page_id, pagination=None):
    dataLoader = LinkedinDataLoader(user_id=user_id, page_id=page_id)
    page = dataLoader.get_page(user_id=user_id, page_id=page_id)
    if page:
        response = dataLoader.fetch_and_save_post(pagination)
        try:
            if len(response["paging"]["links"]) > 0:
                for paging in response["paging"]["links"]:
                    if "rel" in paging.keys():
                        if paging["rel"] == "next":
                            res = linkedin_sync_post( user_id=user_id, page_id=page_id, pagination=paging["href"])
        except Exception as exc:
            log.info(exc)


@shared_task(bind=True, name=settings.LINKEDIN_ACCOUNT_DELETE_TASK)
def delete_linkedin_acc(self, data=None):
    log.info("linkedin_account_delete", data)
    if data:
        user_id = data.get('auth_user_id')
        page_id = data.get('page_id')
        dataLoader = LinkedinDataLoader(user_id=user_id, page_id=page_id)
        page = dataLoader.get_page(user_id=user_id, page_id=page_id)
        if page:
            try:
                page.accountmetrics_set.all().delete()
                page.accountobject_set.all().delete()
                page.delete()
                Cacher.delete(f"stat_health_{user_id}")
            except Exception as msg:
                log.info(msg)


@shared_task(bind=True, name=settings.LINKEDIN_PAGE_DELETE_TASK)
def delete_linkedin_page(self, data=None):
    log.info("linkedin_page_delete", data)
    if data:
        user_id = data.get('auth_user_id')
        page_id = data.get('page_id')
        dataLoader = LinkedinDataLoader(user_id=user_id, page_id=page_id)
        page = dataLoader.get_page(user_id=user_id, page_id=page_id)
        if page:
            try:
                page.accountmetrics_set.all().delete()
                page.accountobject_set.all().delete()
                page.delete()
                Cacher.delete(f"stat_health_{user_id}")
            except Exception as msg:
                log.info(msg)