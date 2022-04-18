import time

from celery import shared_task
from django.conf import settings
from datetime import datetime
from webapp.apps.metrics.data_loader.twitter import TwitterDataLoader
from webapp.apps.api.cache import Cacher
import logging

log = logging.getLogger("twitter")

@shared_task(bind=True, name=settings.TWITTER_ACCOUNT_SYNC_ACTION_TASK, max_retries=1)
def twitter_sync_action_task(self, data=None):
    log.info("twitter_sync_action_task")
    log.info(data)
    if data:
        dataLoader = TwitterDataLoader(user_id=data['auth_user_id'], page_id=data['social_account_id'])
        page = dataLoader.get_page(user_id=data['auth_user_id'], page_id=data['social_account_id'])
        page.sync_status = "progress"
        page.save()
        # try:
        #     dataLoader.save_page(data=data)
        # except Exception as exc:
        #     log.info(exc)
        try:
            dataLoader.fetch_metrics()
        except Exception as exc:
            log.info(exc)
        page = dataLoader.get_page(user_id=data['auth_user_id'], page_id=data['social_account_id'])
        now = datetime.now()
        page.sync_completed = now.strftime("%Y-%m-%d %H:%M:%S")
        if page.sync_status == "pending" or page.sync_status == "progress":
            page.error = ""
            page.sync_status = "ok"
        page.save()
        Cacher.delete(f"stat_health_{data['auth_user_id']}")
        Cacher.delete_pattern(('metrics_{}_*').format(data['auth_user_id']))

@shared_task(bind=True, name=settings.TWITTER_ACCOUNT_SYNC_TASK, max_retries=1)
def twitter_sync_task(self, data=None):
    log.info("twitter_sync")
    log.info(data)
    if data:
        status = data.get("status")
        if status == "active":
            dataLoader = TwitterDataLoader(user_id=data['auth_user_id'], page_id=data['social_account_id'])
            try:
                dataLoader.save_page(data=data)
                twitter_sync_action_task.delay(data)
            except Exception as exc:
                log.info(exc)
            # try:
            #     dataLoader.fetch_metrics()
            # except Exception as exc:
            #     log.info(exc)
            # page = dataLoader.get_page(user_id=data['auth_user_id'], page_id=data['social_account_id'])
            # now = datetime.now()
            # page.sync_completed = now.strftime("%Y-%m-%d %H:%M:%S")
            # page.save()
        if status == "deleted":
            dataLoader = TwitterDataLoader(user_id=data['auth_user_id'], page_id=data['social_account_id'])
            try:
                dataLoader.save_page(data=data)
                Cacher.delete(f"stat_health_{data['auth_user_id']}")
            except Exception as exc:
                log.info(exc)



@shared_task(bind=True, name=settings.TWITTER_ACCOUNT_DELETE_TASK)
def delete_twitter_account(self, data=None):
    log.info("twitter_delete_account", data)
    if data:
        user_id = data.get('auth_user_id')
        page_id = data.get('social_account_id')
        dataLoader = TwitterDataLoader(user_id=user_id, page_id=page_id)
        page = dataLoader.get_page(user_id=user_id, page_id=page_id)
        if page:
            try:
                page.accountmetrics_set.all().delete()
                page.twittermention_set.all().delete()
                page.twitterreply_set.all().delete()
                page.accountobject_set.all().delete()
                page.accountinbox_set.all().delete()
                page.delete()
                Cacher.delete(f"stat_health_{user_id}")
            except Exception as msg:
                log.info(msg)